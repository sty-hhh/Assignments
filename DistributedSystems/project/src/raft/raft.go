package raft

import (
	"bytes"
	"labgob"
	"labrpc"
	"math/rand"
	"sync"
	"sync/atomic"
	"time"
)

const (
	Follower  int = 0
	Candidate int = 1
	Leader    int = 2
)

const (
	ElectionTimeout  = time.Millisecond * 300 // 选举
	HeartBeatTimeout = time.Millisecond * 150 // leader 发送心跳
	ApplyInterval    = time.Millisecond * 100 // apply log
	RPCTimeout       = time.Millisecond * 100
)

type ApplyMsg struct {
	CommandValid bool
	Command      interface{}
	CommandIndex int
}

// 日志结构
type LogEntry struct {
	Term    int
	Command interface{}
}

// Raft 结构
type Raft struct {
	mu        sync.Mutex          // Lock to protect shared access to this peer's state
	peers     []*labrpc.ClientEnd // RPC end points of all peers
	persister *Persister          // Object to hold this peer's persisted state
	me        int                 // this peer's index into peers[]
	dead      int32               // set by Kill()

	// Your data here (2A, 2B, 2C).
	// Look at the paper's Figure 2 for a description of what
	// state a Raft server must maintain.
	role int

	// Persistent state on all servers
	currentTerm int
	voteFor     int        // -1 表示 null
	logEntries  []LogEntry // 从 1 开始, 0 放 lastSnapshot

	// Volatile state on all servers
	commitIndex int // 已知提交的最大 index
	lastApplied int // 此 server 的 log commit

	// Volatile state on leaders
	nextIndex  []int // 下一个要发送的 index
	matchIndex []int // 最大已 match 的 index

	electionTimer       *time.Timer
	appendEntriesTimers []*time.Timer
	applyTimer          *time.Timer
	lastSnapshotIndex   int // 快照中的 index
	lastSnapshotTerm    int
	applyCh             chan ApplyMsg
	notifyApplyCh       chan struct{}
	gid					int
}

// return currentTerm and whether this server
// believes it is the leader.
func (rf *Raft) GetState() (int, bool) {
	var term int
	var isleader bool
	// Your code here (2A).
	rf.mu.Lock()
	defer rf.mu.Unlock()
	term = rf.currentTerm
	isleader = rf.role == Leader
	return term, isleader
}

// save Raft's persistent state to stable storage,
// where it can later be retrieved after a crash and restart.
// see paper's Figure 2 for a description of what should be persistent.
func (rf *Raft) persist() {
	// Your code here (2C).
	data := rf.getPersistData()
	rf.persister.SaveRaftState(data)
}

func (rf *Raft) getPersistData() []byte {
	w := new(bytes.Buffer)
	e := labgob.NewEncoder(w)
	e.Encode(rf.currentTerm)
	e.Encode(rf.voteFor)
	e.Encode(rf.commitIndex)
	e.Encode(rf.lastSnapshotIndex)
	e.Encode(rf.lastSnapshotTerm)
	e.Encode(rf.logEntries)
	data := w.Bytes()
	return data
}

// restore previously persisted state.
func (rf *Raft) readPersist(data []byte) {
	if data == nil || len(data) < 1 {
		return
	}
	// Your code here (2C).
	r := bytes.NewBuffer(data)
	d := labgob.NewDecoder(r)

	var term int
	var voteFor int
	var logs []LogEntry
	var commitIndex, lastSnapshotIndex, lastSnapshotTerm int

	if d.Decode(&term) != nil ||
		d.Decode(&voteFor) != nil ||
		d.Decode(&commitIndex) != nil ||
		d.Decode(&lastSnapshotIndex) != nil ||
		d.Decode(&lastSnapshotTerm) != nil ||
		d.Decode(&logs) != nil {
	} else {
		rf.currentTerm = term
		rf.voteFor = voteFor
		rf.commitIndex = commitIndex
		rf.lastSnapshotIndex = lastSnapshotIndex
		rf.lastSnapshotTerm = lastSnapshotTerm
		rf.logEntries = logs
	}
}

// example RequestVote RPC arguments structure.
// field names must start with capital letters!
type RequestVoteArgs struct {
	// Your data here (2A, 2B).
	Term         int
	CandidateId  int
	LastLogIndex int
	LastLogTerm  int
}

// example RequestVote RPC reply structure.
// field names must start with capital letters!
type RequestVoteReply struct {
	// Your data here (2A).
	Term        int
	VoteGranted bool
}

// RPC: RequestVote
func (rf *Raft) RequestVote(args *RequestVoteArgs, reply *RequestVoteReply) {
	// Your code here (2A, 2B).
	rf.mu.Lock()
	defer rf.mu.Unlock()

	lastLogTerm, lastLogIndex := rf.lastLogTermIndex()
	reply.Term = rf.currentTerm
	reply.VoteGranted = false
	if args.Term < rf.currentTerm { // 投票请求过时
		return
	} else if args.Term == rf.currentTerm { // 在当前 Term 已投票
		if rf.role == Leader || (rf.voteFor != -1 && rf.voteFor != args.CandidateId) {
			return
		} else if rf.voteFor == args.CandidateId {
			reply.VoteGranted = true
			return
		}
	}

	defer rf.persist()
	if args.Term > rf.currentTerm { // 更新当前 Term, 准备投票
		rf.currentTerm = args.Term
		rf.voteFor = -1
		rf.changeRole(Follower)
	}
	// 选取限制
	if lastLogTerm > args.LastLogTerm || (args.LastLogTerm == lastLogTerm && args.LastLogIndex < lastLogIndex) {
		return
	}
	// 投票
	rf.currentTerm = args.Term
	rf.voteFor = args.CandidateId
	reply.VoteGranted = true
	rf.changeRole(Follower)
	rf.resetElectionTimer()
}

// 重置选举定时器
func (rf *Raft) resetElectionTimer() {
	rf.electionTimer.Stop()
	rf.electionTimer.Reset(randElectionTimeout())
}

// 随即设置选举过期时间
func randElectionTimeout() time.Duration {
	r := time.Duration(rand.Int63()) % ElectionTimeout
	return ElectionTimeout + r
}

// 改变角色
func (rf *Raft) changeRole(role int) {
	rf.role = role
	switch role {
	case Follower:
	case Candidate:
		rf.currentTerm += 1
		rf.voteFor = rf.me
		rf.resetElectionTimer()
	case Leader:
		_, lastLogIndex := rf.lastLogTermIndex()
		rf.nextIndex = make([]int, len(rf.peers))
		for i := 0; i < len(rf.peers); i++ {
			rf.nextIndex[i] = lastLogIndex + 1
		}
		rf.matchIndex = make([]int, len(rf.peers))
		rf.matchIndex[rf.me] = lastLogIndex
		rf.resetElectionTimer()
	}
}

// send a RequestVote RPC to a server.
func (rf *Raft) sendRequestVote(server int, args *RequestVoteArgs, reply *RequestVoteReply) bool {
	ok := rf.peers[server].Call("Raft.RequestVote", args, reply)
	return ok
}

// 开始选举
func (rf *Raft) startElection() {
	// 准备开始选举
	rf.mu.Lock()
	rf.resetElectionTimer()
	if rf.role == Leader {
		rf.mu.Unlock()
		return
	}
	rf.changeRole(Candidate) // 选举前更新为 Candidate
	lastLogTerm, lastLogIndex := rf.lastLogTermIndex()
	args := RequestVoteArgs{
		Term:         rf.currentTerm,
		CandidateId:  rf.me,
		LastLogIndex: lastLogIndex,
		LastLogTerm:  lastLogTerm,
	}
	rf.persist()
	rf.mu.Unlock()
	// 发送投票请求
	grantedCount := 1                         // 同意票数
	respondCount := 1                         // 投票总数
	votesCh := make(chan bool, len(rf.peers)) // 每个 peer 的投票结果
	for index := range rf.peers {
		if index == rf.me {
			continue
		}
		go func(ch chan bool, index int) {
			reply := RequestVoteReply{}
			rf.sendRequestVote(index, &args, &reply) // RPC 发送投票请求
			ch <- reply.VoteGranted                  // 获取每个 peer 是否投票同意
			if reply.Term > args.Term {
				rf.mu.Lock()
				if rf.currentTerm < reply.Term { // 5.4.1 Election Restriction: 有更加新的 Term, 直接拒绝
					rf.currentTerm = reply.Term
					rf.changeRole(Follower)
					rf.resetElectionTimer()
					rf.persist()
				}
				rf.mu.Unlock()
			}
		}(votesCh, index)
	}
	for {
		r := <-votesCh // 从 channel 返回每个 peer 的投票结果
		respondCount += 1
		if r {
			grantedCount += 1
		}
		// 直到全部已投票, 或者[同意/不同意]票数过半
		if respondCount == len(rf.peers) || grantedCount > len(rf.peers)/2 || respondCount-grantedCount > len(rf.peers)/2 {
			break
		}
	}
	// 同意票数未过半, 直接结束
	if grantedCount <= len(rf.peers)/2 {
		return
	}
	// 选举成为 Leader
	rf.mu.Lock()
	defer rf.mu.Unlock()
	if rf.currentTerm == args.Term && rf.role == Candidate {
		rf.changeRole(Leader)
		rf.persist()
	}
	if rf.role == Leader {
		rf.resetHeartBeatTimers() // 心跳计时器清零
	}
}

// 添加日志
type AppendEntriesArgs struct {
	Term         int
	LeaderId     int
	PrevLogIndex int
	PervLogTerm  int
	Entries      []LogEntry
	LeaderCommit int
}

type AppendEntriesReply struct {
	Term      int
	Success   bool
	NextIndex int
}

func (rf *Raft) getNextIndex() int {
	_, idx := rf.lastLogTermIndex()
	return idx + 1
}

func (rf *Raft) outOfOrderAppendEntries(args *AppendEntriesArgs) bool {
	argsLastIndex := args.PrevLogIndex + len(args.Entries)
	lastTerm, lastIndex := rf.lastLogTermIndex()
	if argsLastIndex < lastIndex && lastTerm == args.Term {
		return true
	}
	return false
}

// RPC: AppendEntries
func (rf *Raft) AppendEntries(args *AppendEntriesArgs, reply *AppendEntriesReply) {
	rf.mu.Lock()
	defer rf.mu.Unlock()
	defer rf.persist()
	if rf.currentTerm > args.Term {
		return
	}
	reply.Term = rf.currentTerm
	rf.currentTerm = args.Term
	rf.changeRole(Follower)
	rf.resetElectionTimer()
	_, lastLogIndex := rf.lastLogTermIndex()

	if args.PrevLogIndex > lastLogIndex { // 缺少中间的 log
		reply.Success = false
		reply.NextIndex = rf.getNextIndex()
	} else if args.PrevLogIndex < rf.lastSnapshotIndex { // lastsnapshotindex 应该已被 apply, 正常情况不该发生
		reply.Success = false
		reply.NextIndex = rf.lastSnapshotIndex + 1
	} else if args.PrevLogIndex == rf.lastSnapshotIndex { // 上一个刚好是 snapshot
		if rf.outOfOrderAppendEntries(args) { // 乱序的请求返回失败
			reply.Success = false
			reply.NextIndex = 0
		} else {
			reply.Success = true
			rf.logEntries = append(rf.logEntries[:1], args.Entries...) // 保留 logEntries[0]
			reply.NextIndex = rf.getNextIndex()
		}
	} else if rf.getLogByIndex(args.PrevLogIndex).Term == args.PervLogTerm {
		// args.PrevLogIndex > rf.lastSnapshotIndex
		// 1) 刚好是后续的 log
		if rf.outOfOrderAppendEntries(args) { // 乱序的请求返回失败
			reply.Success = false
			reply.NextIndex = 0
		} else {
			reply.Success = true
			rf.logEntries = append(rf.logEntries[0:rf.getRealIdxByIndex(args.PrevLogIndex)+1], args.Entries...)
			reply.NextIndex = rf.getNextIndex()
		}
	} else {
		// 2) 需要回退
		reply.Success = false
		term := rf.getLogByIndex(args.PrevLogIndex).Term // 尝试跳过一个 Term
		idx := args.PrevLogIndex
		for idx > rf.commitIndex && idx > rf.lastSnapshotIndex && rf.getLogByIndex(idx).Term == term {
			idx -= 1
		}
		reply.NextIndex = idx + 1 // 新 Term 的第一个 index
	}
	// 成功提交
	if reply.Success && rf.commitIndex < args.LeaderCommit {
		rf.commitIndex = args.LeaderCommit
		rf.notifyApplyCh <- struct{}{}
	}
}

func (rf *Raft) getAppendLogs(peerIdx int) (prevLogIndex, prevLogTerm int, res []LogEntry) {
	nextIdx := rf.nextIndex[peerIdx]
	lastLogTerm, lastLogIndex := rf.lastLogTermIndex()
	if nextIdx <= rf.lastSnapshotIndex || nextIdx > lastLogIndex {
		// 没有需要发送的 log
		prevLogIndex = lastLogIndex
		prevLogTerm = lastLogTerm
		return
	}
	res = append([]LogEntry{}, rf.logEntries[rf.getRealIdxByIndex(nextIdx):]...)
	prevLogIndex = nextIdx - 1
	if prevLogIndex == rf.lastSnapshotIndex {
		prevLogTerm = rf.lastSnapshotTerm
	} else {
		prevLogTerm = rf.getLogByIndex(prevLogIndex).Term
	}
	return
}

// 准备要发送的日志
func (rf *Raft) getAppendEntriesArgs(peerIdx int) AppendEntriesArgs {
	prevLogIndex, prevLogTerm, logs := rf.getAppendLogs(peerIdx)
	args := AppendEntriesArgs{
		Term:         rf.currentTerm,
		LeaderId:     rf.me,
		PrevLogIndex: prevLogIndex,
		PervLogTerm:  prevLogTerm,
		Entries:      logs,
		LeaderCommit: rf.commitIndex,
	}
	return args
}

// 心跳计时器清零
func (rf *Raft) resetHeartBeatTimers() {
	for i := range rf.appendEntriesTimers {
		rf.appendEntriesTimers[i].Stop()
		rf.appendEntriesTimers[i].Reset(0)
	}
}

// 心跳计时器设置
func (rf *Raft) resetHeartBeatTimer(peerIdx int) {
	rf.appendEntriesTimers[peerIdx].Stop()
	rf.appendEntriesTimers[peerIdx].Reset(HeartBeatTimeout)
}

// send an AppendEntries RPC to a server.
func (rf *Raft) sendAppendEntries(peerIdx int) {
	RPCTimer := time.NewTimer(RPCTimeout)
	defer RPCTimer.Stop()

	for !rf.killed() {
		rf.mu.Lock()
		if rf.role != Leader { // 不是 Leader, 直接结束
			rf.resetHeartBeatTimer(peerIdx)
			rf.mu.Unlock()
			return
		}
		args := rf.getAppendEntriesArgs(peerIdx)
		rf.resetHeartBeatTimer(peerIdx)
		rf.mu.Unlock()

		RPCTimer.Stop()
		RPCTimer.Reset(RPCTimeout)
		reply := AppendEntriesReply{} // RPC 返回reply
		resCh := make(chan bool, 1)   // call result
		go func(args *AppendEntriesArgs, reply *AppendEntriesReply) {
			ok := rf.peers[peerIdx].Call("Raft.AppendEntries", args, reply)
			if !ok {
				time.Sleep(time.Millisecond * 10)
			}
			resCh <- ok
		}(&args, &reply)

		select {
		case <-RPCTimer.C: // RPC 超时
			continue
		case ok := <-resCh:
			if !ok { // RPC 失败
				continue
			}
		}
		// call ok, check reply
		rf.mu.Lock()
		if rf.currentTerm != args.Term { // 不是 Leader, 或者 Term 不匹配
			rf.mu.Unlock()
			return
		} else if reply.Term > rf.currentTerm { // Election Restriction: 有更加新的 Term, 直接拒绝
			rf.changeRole(Follower)
			rf.resetElectionTimer()
			rf.currentTerm = reply.Term
			rf.persist()
			rf.mu.Unlock()
			return
		} else if reply.Success { // reply 成功
			if reply.NextIndex > rf.nextIndex[peerIdx] {
				rf.nextIndex[peerIdx] = reply.NextIndex
				rf.matchIndex[peerIdx] = reply.NextIndex - 1
			}
			if len(args.Entries) > 0 && args.Entries[len(args.Entries)-1].Term == rf.currentTerm {
				// 只 commit 自己 term 的 index
				rf.updateCommitIndex()
			}
			rf.persist()
			rf.mu.Unlock()
			return
		} else if reply.NextIndex != 0 { // reply 失败
			if reply.NextIndex > rf.lastSnapshotIndex {
				// need retry
				rf.nextIndex[peerIdx] = reply.NextIndex
				rf.mu.Unlock()
				continue
			} else {
				// send snapshot rpc
				go rf.sendInstallSnapshot(peerIdx)
				rf.mu.Unlock()
				return
			}
		} else {
			// 乱序
			rf.mu.Unlock()
		}
	}
}

// 更新 commitIndex
func (rf *Raft) updateCommitIndex() {
	hasCommit := false
	for i := rf.commitIndex + 1; i <= rf.lastSnapshotIndex+len(rf.logEntries); i++ {
		count := 0
		for _, m := range rf.matchIndex {
			if m >= i {
				count += 1
				if count > len(rf.peers)/2 {
					rf.commitIndex = i
					hasCommit = true
					break
				}
			}
		}
		if rf.commitIndex != i { // 后续的不需要再判断
			break
		}
	}
	if hasCommit {		// 成功提交
		rf.notifyApplyCh <- struct{}{}
	}
}

// 日志压缩
type InstallSnapshotArgs struct {
	Term              int
	LeaderId          int
	LastIncludedIndex int
	LastIncludedTerm  int
	Data              []byte
}

type InstallSnapshotReply struct {
	Term int
}

// KV 用: 保存 persistData 和 snapshot
func (rf *Raft) Snapshot(logIndex int, snapshot []byte) {
	rf.mu.Lock()
	defer rf.mu.Unlock()
	if logIndex <= rf.lastSnapshotIndex {
		return
	}
	if logIndex > rf.commitIndex {
		panic("logindex > rf.commitdex")
	}
	// logindex 一定在 raft.logEntries 中存在
	lastLog := rf.getLogByIndex(logIndex)
	rf.logEntries = rf.logEntries[rf.getRealIdxByIndex(logIndex):]
	rf.lastSnapshotIndex = logIndex
	rf.lastSnapshotTerm = lastLog.Term
	persistData := rf.getPersistData()
	rf.persister.SaveStateAndSnapshot(persistData, snapshot)
}

// RPC: InstallSnapshot
func (rf *Raft) InstallSnapshot(args *InstallSnapshotArgs, reply *InstallSnapshotReply) {
	rf.mu.Lock()
	defer rf.mu.Unlock()

	reply.Term = rf.currentTerm
	if args.Term < rf.currentTerm || rf.lastSnapshotIndex >= args.LastIncludedIndex { // rpc 过时, 或者 snapshotindex 错误
		return
	} else if args.Term > rf.currentTerm || rf.role != Follower {
		rf.currentTerm = args.Term
		rf.changeRole(Follower)
		rf.resetElectionTimer()
		defer rf.persist()
	}
	// success
	snapShotLen := args.LastIncludedIndex - rf.lastSnapshotIndex // 本次 snapshot 长度
	if snapShotLen >= len(rf.logEntries) {
		rf.logEntries = make([]LogEntry, 1)
		rf.logEntries[0].Term = args.LastIncludedTerm
	} else {
		rf.logEntries = rf.logEntries[snapShotLen:] // 保留 snapshot 之后的 log
	}
	rf.lastSnapshotIndex = args.LastIncludedIndex
	rf.lastSnapshotTerm = args.LastIncludedTerm
	rf.persister.SaveStateAndSnapshot(rf.getPersistData(), args.Data)
}

// send an InstallSnapshot RPC to a server.
func (rf *Raft) sendInstallSnapshot(peerIdx int) {
	rf.mu.Lock()
	args := InstallSnapshotArgs{
		Term:              rf.currentTerm,
		LeaderId:          rf.me,
		LastIncludedIndex: rf.lastSnapshotIndex,
		LastIncludedTerm:  rf.lastSnapshotTerm,
		Data:              rf.persister.ReadSnapshot(),
	}
	rf.mu.Unlock()
	timer := time.NewTimer(RPCTimeout)
	defer timer.Stop()

	for !rf.killed() {
		timer.Stop()
		timer.Reset(RPCTimeout)
		okCh := make(chan bool, 1)
		reply := InstallSnapshotReply{}
		go func() {
			r := rf.peers[peerIdx].Call("Raft.InstallSnapshot", &args, &reply)
			if !r {
				time.Sleep(time.Millisecond * 10)
			}
			okCh <- r
		}()

		ok := false
		select {
		case <-timer.C: // RPC 超时
			continue
		case ok = <-okCh:
			if !ok { // RPC 失败
				continue
			}
		}
		// ok == true
		rf.mu.Lock()
		defer rf.mu.Unlock()
		if rf.currentTerm != args.Term || rf.role != Leader {
			return
		} else if reply.Term > rf.currentTerm {
			rf.changeRole(Follower)
			rf.resetElectionTimer()
			rf.currentTerm = reply.Term
			rf.persist()
			return
		}
		// success
		if args.LastIncludedIndex > rf.matchIndex[peerIdx] {
			rf.matchIndex[peerIdx] = args.LastIncludedIndex
		}
		if args.LastIncludedIndex+1 > rf.nextIndex[peerIdx] {
			rf.nextIndex[peerIdx] = args.LastIncludedIndex + 1
		}
		return
	}
}

// Start: 用于 config / test / kvraft
func (rf *Raft) Start(command interface{}) (int, int, bool) {
	// Your code here (2B).
	rf.mu.Lock()
	defer rf.mu.Unlock()
	_, lastIndex := rf.lastLogTermIndex()
	index := lastIndex + 1
	term := rf.currentTerm
	isLeader := rf.role == Leader
	if isLeader {	// Leader 才能写 log
		rf.logEntries = append(rf.logEntries, LogEntry{
			Term:    rf.currentTerm,
			Command: command,
		})
		rf.matchIndex[rf.me] = index
		rf.persist()
	}
	rf.resetHeartBeatTimers() // 心跳计时器清零
	return index, term, isLeader
}

// the tester doesn't halt goroutines created by Raft after each test,
// but it does call the Kill() method. your code can use killed() to
// check whether Kill() has been called. the use of atomic avoids the
// need for a lock.
//
// the issue is that long-running goroutines use memory and may chew
// up CPU time, perhaps causing later tests to fail and generating
// confusing debug output. any goroutine with a long-running loop
// should call killed() to check whether it should stop.
func (rf *Raft) Kill() {
	atomic.StoreInt32(&rf.dead, 1)
}

func (rf *Raft) killed() bool {
	z := atomic.LoadInt32(&rf.dead)
	return z == 1
}

func (rf *Raft) lastLogTermIndex() (int, int) {
	term := rf.logEntries[len(rf.logEntries)-1].Term
	index := rf.lastSnapshotIndex + len(rf.logEntries) - 1
	return term, index
}

func (rf *Raft) getLogByIndex(logIndex int) LogEntry {
	return rf.logEntries[rf.getRealIdxByIndex(logIndex)]
}

func (rf *Raft) getRealIdxByIndex(logIndex int) int {
	idx := logIndex - rf.lastSnapshotIndex
	return idx
}

func (rf *Raft) startApplyLogs() {
	defer rf.applyTimer.Reset(ApplyInterval)

	rf.mu.Lock()
	var msgs []ApplyMsg
	if rf.lastApplied < rf.lastSnapshotIndex {
		msgs = make([]ApplyMsg, 0, 1)
		msgs = append(msgs, ApplyMsg{
			CommandValid: false,
			Command:      "installSnapShot",
			CommandIndex: rf.lastSnapshotIndex,
		})
	} else if rf.commitIndex <= rf.lastApplied {
		// snapShot 没有更新 commitIndex
		msgs = make([]ApplyMsg, 0)
	} else {
		msgs = make([]ApplyMsg, 0, rf.commitIndex-rf.lastApplied)
		for i := rf.lastApplied + 1; i <= rf.commitIndex; i++ {
			msgs = append(msgs, ApplyMsg{
				CommandValid: true,
				Command:      rf.getLogByIndex(i).Command,
				CommandIndex: i,
			})
		}
	}
	rf.mu.Unlock()

	for _, msg := range msgs {
		rf.applyCh <- msg
		rf.mu.Lock()
		rf.lastApplied = msg.CommandIndex
		rf.mu.Unlock()
	}
}

// the service or tester wants to create a Raft server. the ports
// of all the Raft servers (including this one) are in peers[]. this
// server's port is peers[me]. all the servers' peers[] arrays
// have the same order. persister is a place for this server to
// save its persistent state, and also initially holds the most
// recent saved state, if any. applyCh is a channel on which the
// tester or service expects Raft to send ApplyMsg messages.
// Make() must return quickly, so it should start goroutines
// for any long-running work.
func Make(peers []*labrpc.ClientEnd, me int, persister *Persister, applyCh chan ApplyMsg, gid ...int) *Raft {
	rf := &Raft{}
	rf.peers = peers
	rf.persister = persister
	rf.me = me
	rf.applyCh = applyCh

	if len(gid) != 0 {
		rf.gid = gid[0]
	} else {
		rf.gid = -1
	}

	// Your initialization code here (2A, 2B, 2C).
	rf.currentTerm = 0
	rf.voteFor = -1
	rf.role = Follower
	rf.logEntries = make([]LogEntry, 1)
	rf.readPersist(persister.ReadRaftState())

	rf.electionTimer = time.NewTimer(randElectionTimeout())
	rf.appendEntriesTimers = make([]*time.Timer, len(rf.peers))
	for i := range rf.peers {
		rf.appendEntriesTimers[i] = time.NewTimer(HeartBeatTimeout)
	}
	rf.applyTimer = time.NewTimer(ApplyInterval)
	rf.notifyApplyCh = make(chan struct{}, 100)

	// apply log
	go func() {
		for !rf.killed() {
			select {
			case <-rf.applyTimer.C:
				rf.notifyApplyCh <- struct{}{}
			case <-rf.notifyApplyCh:
				rf.startApplyLogs()
			}
		}
	}()
	// start election
	go func() {
		for !rf.killed() {
			<-rf.electionTimer.C
			rf.startElection()
		}
	}()
	// leader send logs
	for i := range peers {
		if i == rf.me {
			continue
		}
		go func(index int) {
			for !rf.killed() {
				<-rf.appendEntriesTimers[index].C
				rf.sendAppendEntries(index)
			}
		}(i)
	}

	return rf
}
