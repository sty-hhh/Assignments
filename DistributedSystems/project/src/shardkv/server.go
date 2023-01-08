package shardkv

import (
	"bytes"
	"labgob"
	"labrpc"
	"raft"
	"shardmaster"
	"sync"
	"time"
)

const (
	PullConfigInterval       = time.Millisecond * 100
	PullShardsInterval       = time.Millisecond * 200
	WaitCmdTimeOut           = time.Millisecond * 500
	ReqCleanShardDataTimeOut = time.Millisecond * 500
)

type Op struct {
	Key       string
	Value     string
	Method    string
	ClientId  int64
	MsgId     int64
	ReqId     int64
	ConfigNum int
}

type NotifyMsg struct {
	Err   Err
	Value string
}

type ShardKV struct {
	mu           sync.Mutex
	me           int
	rf           *raft.Raft
	applyCh      chan raft.ApplyMsg
	make_end     func(string) *labrpc.ClientEnd
	gid          int
	masters      []*labrpc.ClientEnd
	maxraftstate int // snapshot if log grows this big

	// Your definitions here.
	config        shardmaster.Config // the latest config
	oldConfig     shardmaster.Config
	notifyCh      map[int64]chan NotifyMsg             // notify cmd done
	lastMsgIdx    [shardmaster.NShards]map[int64]int64 // clientId -> msgId map
	ownShards     map[int]bool
	data          [shardmaster.NShards]map[string]string // kv per shard
	waitShardIds  map[int]bool
	historyShards map[int]map[int]MergeShardData // configNum -> shard -> data
	mck           *shardmaster.Clerk

	stopCh          chan struct{}
	persister       *raft.Persister
	pullConfigTimer *time.Timer
	pullShardsTimer *time.Timer
}

// RPC: Get
func (kv *ShardKV) Get(args *GetArgs, reply *GetReply) {
	op := Op{
		MsgId:     args.MsgId,
		ReqId:     nrand(),
		Key:       args.Key,
		Method:    "Get",
		ClientId:  args.ClientId,
		ConfigNum: args.ConfigNum,
	}
	res := kv.waitCmd(op)
	reply.Err = res.Err
	reply.Value = res.Value
}

// RPC: PutAppend
func (kv *ShardKV) PutAppend(args *PutAppendArgs, reply *PutAppendReply) {
	op := Op{
		MsgId:     args.MsgId,
		ReqId:     nrand(),
		Key:       args.Key,
		Value:     args.Value,
		Method:    args.Op,
		ClientId:  args.ClientId,
		ConfigNum: args.ConfigNum,
	}
	reply.Err = kv.waitCmd(op).Err
}

// RPC: Delete
func (kv *ShardKV) Delete(args *DeleteArgs, reply *DeleteReply) {
	op := Op{
		MsgId:     args.MsgId,
		ReqId:     nrand(),
		Key:       args.Key,
		Method:    "Delete",
		ClientId:  args.ClientId,
		ConfigNum: args.ConfigNum,
	}
	reply.Err = kv.waitCmd(op).Err
}

func (kv *ShardKV) removeCh(id int64) {
	kv.mu.Lock()
	delete(kv.notifyCh, id)
	kv.mu.Unlock()
}

// 将 RPC 请求的 Command 通过 Raft 写入 Logentries, 等待 Command 执行完成返回结果
func (kv *ShardKV) waitCmd(op Op) (res NotifyMsg) {
	ch := make(chan NotifyMsg, 1)
	kv.mu.Lock()
	// 这里不检查 wait shard id
	// 若是新 leader，需要想办法产生本 term 的日志
	if op.ConfigNum == 0 || op.ConfigNum < kv.config.Num {
		res.Err = ErrWrongGroup
		kv.mu.Unlock()
		return
	}
	kv.mu.Unlock()
	// 启动 raft
	_, _, isLeader := kv.rf.Start(op)
	if !isLeader {
		res.Err = ErrWrongLeader
		return
	}
	kv.mu.Lock()
	kv.notifyCh[op.ReqId] = ch
	kv.mu.Unlock()
	t := time.NewTimer(WaitCmdTimeOut)
	defer t.Stop()
	select {
	case res = <-ch:
		kv.removeCh(op.ReqId)
		return
	case <-t.C:
		kv.removeCh(op.ReqId)
		res.Err = ErrTimeOut
		return
	}
}

func (kv *ShardKV) dataGet(key string) (err Err, val string) {
	if v, ok := kv.data[key2shard(key)][key]; ok {
		err = OK
		val = v
		return
	} else {
		err = ErrNoKey
		return err, ""
	}
}

// 等待 msg -> 执行 Command
func (kv *ShardKV) waitApplyCh() {
	for {
		select {
		case <-kv.stopCh:
			return
		case msg := <-kv.applyCh:
			if !msg.CommandValid {
				kv.applySnapshot()
				continue
			}
			if op, ok := msg.Command.(Op); ok {
				kv.applyOp(msg, op)
			} else if config, ok := msg.Command.(shardmaster.Config); ok {
				kv.applyConfig(msg, config)
			} else if mergeData, ok := msg.Command.(MergeShardData); ok {
				kv.applyMergeShardData(msg, mergeData)
			} else if cleanUp, ok := msg.Command.(CleanShardDataArgs); ok {
				kv.applyCleanUp(msg, cleanUp)
			} else {
				panic("applyerr")
			}
		}
	}
}

func (kv *ShardKV) applySnapshot() {
	kv.mu.Lock()
	kv.readSnapShotData(kv.persister.ReadSnapshot())
	kv.mu.Unlock()
}

func (kv *ShardKV) applyOp(msg raft.ApplyMsg, op Op) {
	msgIdx := msg.CommandIndex
	kv.mu.Lock()
	defer kv.mu.Unlock()
	shardId := key2shard(op.Key)
	isRepeated := kv.isRepeated(shardId, op.ClientId, op.MsgId)
	if kv.configReady(op.ConfigNum, op.Key) == OK {
		switch op.Method {
		case "Get":
		case "Put":
			if !isRepeated {
				kv.data[shardId][op.Key] = op.Value
				kv.lastMsgIdx[shardId][op.ClientId] = op.MsgId
			}
		case "Append":
			if !isRepeated {
				_, v := kv.dataGet(op.Key)
				kv.data[shardId][op.Key] = v + op.Value
				kv.lastMsgIdx[shardId][op.ClientId] = op.MsgId
			}
		case "Delete":
			if !isRepeated {
				delete(kv.data[shardId], op.Key)
				kv.lastMsgIdx[shardId][op.ClientId] = op.MsgId
			}
		default:
			panic("unknown method")
		}
		kv.saveSnapshot(msgIdx)
		if ch, ok := kv.notifyCh[op.ReqId]; ok {
			nm := NotifyMsg{Err: OK}
			if op.Method == "Get" {
				nm.Err, nm.Value = kv.dataGet(op.Key)
			}
			ch <- nm
		}
	} else {
		// config not ready
		if ch, ok := kv.notifyCh[op.ReqId]; ok {
			ch <- NotifyMsg{Err: ErrWrongGroup}
		}
	}
}

func (kv *ShardKV) applyConfig(msg raft.ApplyMsg, config shardmaster.Config) {
	kv.mu.Lock()
	defer kv.mu.Unlock()
	if config.Num <= kv.config.Num {
		kv.saveSnapshot(msg.CommandIndex)
		return
	}
	if config.Num != kv.config.Num+1 {
		panic("applyConfig err")
	}
	oldConfig := kv.config.Copy()
	deleteShardIds := make([]int, 0, shardmaster.NShards)
	ownShardIds := make([]int, 0, shardmaster.NShards)
	newShardIds := make([]int, 0, shardmaster.NShards)
	for i := 0; i < shardmaster.NShards; i++ {
		if config.Shards[i] == kv.gid {
			ownShardIds = append(ownShardIds, i)
			if oldConfig.Shards[i] != kv.gid {
				newShardIds = append(newShardIds, i)
			}
		} else if oldConfig.Shards[i] == kv.gid {
			// config.Shards[i] != kv.gid
			deleteShardIds = append(deleteShardIds, i)
		}
	}
	d := make(map[int]MergeShardData)
	for _, shardId := range deleteShardIds {
		mergeShardData := MergeShardData{
			ConfigNum:  oldConfig.Num,
			ShardNum:   shardId,
			Data:       kv.data[shardId],
			MsgIndexes: kv.lastMsgIdx[shardId],
		}
		d[shardId] = mergeShardData
		kv.data[shardId] = make(map[string]string)
		kv.lastMsgIdx[shardId] = make(map[int64]int64)
	}
	kv.historyShards[oldConfig.Num] = d
	kv.ownShards = make(map[int]bool)
	for _, shardId := range ownShardIds {
		kv.ownShards[shardId] = true
	}
	kv.waitShardIds = make(map[int]bool)
	if oldConfig.Num != 0 {
		for _, shardId := range newShardIds {
			kv.waitShardIds[shardId] = true
		}
	}
	kv.config = config.Copy()
	kv.oldConfig = oldConfig
	kv.saveSnapshot(msg.CommandIndex)
}

func (kv *ShardKV) applyMergeShardData(msg raft.ApplyMsg, data MergeShardData) {
	kv.mu.Lock()
	defer kv.mu.Unlock()
	defer kv.saveSnapshot(msg.CommandIndex)
	if kv.config.Num != data.ConfigNum+1 {
		return
	}
	if _, ok := kv.waitShardIds[data.ShardNum]; !ok {
		return
	}
	kv.data[data.ShardNum] = make(map[string]string)
	kv.lastMsgIdx[data.ShardNum] = make(map[int64]int64)
	for k, v := range data.Data {
		kv.data[data.ShardNum][k] = v
	}
	for k, v := range data.MsgIndexes {
		kv.lastMsgIdx[data.ShardNum][k] = v
	}
	delete(kv.waitShardIds, data.ShardNum)
	go kv.reqCleanShardData(kv.oldConfig, data.ShardNum)
}

func (kv *ShardKV) applyCleanUp(msg raft.ApplyMsg, data CleanShardDataArgs) {
	kv.mu.Lock()
	defer kv.mu.Unlock()
	if kv.historyDataExist(data.ConfigNum, data.ShardNum) {
		delete(kv.historyShards[data.ConfigNum], data.ShardNum)
	}
	kv.saveSnapshot(msg.CommandIndex)
}

func (kv *ShardKV) isRepeated(shardId int, clientId int64, id int64) bool {
	if val, ok := kv.lastMsgIdx[shardId][clientId]; ok {
		return val == id
	}
	return false
}

func (kv *ShardKV) saveSnapshot(logIndex int) {
	if kv.maxraftstate == -1 || kv.persister.RaftStateSize() < kv.maxraftstate {
		return
	}
	data := kv.genSnapshotData()
	kv.rf.Snapshot(logIndex, data)
}

func (kv *ShardKV) genSnapshotData() []byte {
	w := new(bytes.Buffer)
	e := labgob.NewEncoder(w)
	e.Encode(kv.data)
	e.Encode(kv.lastMsgIdx)
	e.Encode(kv.waitShardIds)
	e.Encode(kv.historyShards)
	e.Encode(kv.config)
	e.Encode(kv.oldConfig)
	e.Encode(kv.ownShards)
	data := w.Bytes()
	return data
}

func (kv *ShardKV) readSnapShotData(data []byte) {
	if data == nil || len(data) < 1 { // bootstrap without any state?
		return
	}
	r := bytes.NewBuffer(data)
	d := labgob.NewDecoder(r)
	var kvData [shardmaster.NShards]map[string]string
	var lastMsgIdx [shardmaster.NShards]map[int64]int64
	var waitShardIds map[int]bool
	var historyShards map[int]map[int]MergeShardData
	var config shardmaster.Config
	var oldConfig shardmaster.Config
	var ownShards map[int]bool
	if d.Decode(&kvData) != nil ||
		d.Decode(&lastMsgIdx) != nil ||
		d.Decode(&waitShardIds) != nil ||
		d.Decode(&historyShards) != nil ||
		d.Decode(&config) != nil ||
		d.Decode(&oldConfig) != nil ||
		d.Decode(&ownShards) != nil {
	} else {
		kv.data = kvData
		kv.lastMsgIdx = lastMsgIdx
		kv.waitShardIds = waitShardIds
		kv.historyShards = historyShards
		kv.config = config
		kv.oldConfig = oldConfig
		kv.ownShards = ownShards
	}
}

func (kv *ShardKV) configReady(configNum int, key string) Err {
	if configNum == 0 || configNum != kv.config.Num {
		return ErrWrongGroup
	}
	shardId := key2shard(key)
	if _, ok := kv.ownShards[shardId]; !ok {
		return ErrWrongGroup
	}
	if _, ok := kv.waitShardIds[shardId]; ok {
		return ErrWrongGroup
	}
	return OK
}

// the tester calls Kill() when a ShardKV instance won't be needed again.
func (kv *ShardKV) Kill() {
	kv.rf.Kill()
	close(kv.stopCh)
}

func (kv *ShardKV) pullConfig() {
	for {
		select {
		case <-kv.stopCh:
			return
		case <-kv.pullConfigTimer.C:
			_, isLeader := kv.rf.GetState()
			if !isLeader {
				kv.pullConfigTimer.Reset(PullConfigInterval)
				break
			}
			kv.mu.Lock()
			lastNum := kv.config.Num
			kv.mu.Unlock()
			config := kv.mck.Query(lastNum + 1)
			if config.Num == lastNum+1 {
				// 找到新的 config
				kv.mu.Lock()
				if len(kv.waitShardIds) == 0 && kv.config.Num+1 == config.Num {
					kv.mu.Unlock()
					kv.rf.Start(config.Copy())
				} else {
					kv.mu.Unlock()
				}
			}
			kv.pullConfigTimer.Reset(PullConfigInterval)
		}
	}
}

func (kv *ShardKV) FetchShardData(args *FetchShardDataArgs, reply *FetchShardDataReply) {
	kv.mu.Lock()
	defer kv.mu.Unlock()
	if args.ConfigNum >= kv.config.Num {
		return
	}
	if configData, ok := kv.historyShards[args.ConfigNum]; ok {
		if shardData, ok := configData[args.ShardNum]; ok {
			reply.Success = true
			reply.Data = make(map[string]string)
			reply.MsgIndexes = make(map[int64]int64)
			for k, v := range shardData.Data {
				reply.Data[k] = v
			}
			for k, v := range shardData.MsgIndexes {
				reply.MsgIndexes[k] = v
			}
		}
	}
}

func (kv *ShardKV) historyDataExist(configNum int, shardId int) bool {
	if _, ok := kv.historyShards[configNum]; ok {
		if _, ok = kv.historyShards[configNum][shardId]; ok {
			return true
		}
	}
	return false
}

func (kv *ShardKV) CleanShardData(args *CleanShardDataArgs, reply *CleanShardDataReply) {
	kv.mu.Lock()
	if args.ConfigNum >= kv.config.Num { // 此时没有数据
		kv.mu.Unlock()
		return
	}
	kv.mu.Unlock()
	_, _, isLeader := kv.rf.Start(*args)
	if !isLeader {
		return
	}
	// 简单处理
	for i := 0; i < shardmaster.NShards; i++ {
		kv.mu.Lock()
		exist := kv.historyDataExist(args.ConfigNum, args.ShardNum)
		kv.mu.Unlock()
		if !exist {
			reply.Success = true
			return
		}
		time.Sleep(time.Millisecond * 20)
	}
}

func (kv *ShardKV) reqCleanShardData(config shardmaster.Config, shardId int) {
	configNum := config.Num
	args := &CleanShardDataArgs{
		ConfigNum: configNum,
		ShardNum:  shardId,
	}
	t := time.NewTimer(ReqCleanShardDataTimeOut)
	defer t.Stop()
	for {
		for _, s := range config.Groups[config.Shards[shardId]] {
			reply := &CleanShardDataReply{}
			srv := kv.make_end(s)
			done := make(chan bool, 1)
			r := false
			go func(args *CleanShardDataArgs, reply *CleanShardDataReply) {
				done <- srv.Call("ShardKV.CleanShardData", args, reply)
			}(args, reply)
			t.Reset(ReqCleanShardDataTimeOut)
			select {
			case <-kv.stopCh:
				return
			case r = <-done:
				if r && reply.Success {
					return
				}
			case <-t.C: // 超时重试
			}
		}
		kv.mu.Lock()
		if kv.config.Num != configNum+1 || len(kv.waitShardIds) == 0 {
			kv.mu.Unlock()
			break
		}
		kv.mu.Unlock()
	}
}

func (kv *ShardKV) pullShards() {
	for {
		select {
		case <-kv.stopCh:
			return
		case <-kv.pullShardsTimer.C:
			_, isLeader := kv.rf.GetState()
			if isLeader {
				kv.mu.Lock()
				for shardId := range kv.waitShardIds {
					go kv.pullShard(shardId, kv.oldConfig)
				}
				kv.mu.Unlock()
			}
			kv.pullShardsTimer.Reset(PullShardsInterval)
		}
	}
}

func (kv *ShardKV) pullShard(shardId int, config shardmaster.Config) {
	args := FetchShardDataArgs{
		ConfigNum: config.Num,
		ShardNum:  shardId,
	}
	for _, s := range config.Groups[config.Shards[shardId]] {
		srv := kv.make_end(s)
		reply := FetchShardDataReply{}
		if ok := srv.Call("ShardKV.FetchShardData", &args, &reply); ok {
			if reply.Success {
				kv.mu.Lock()
				if _, ok = kv.waitShardIds[shardId]; ok && kv.config.Num == config.Num+1 {
					replyCopy := reply.Copy()
					mergeArgs := MergeShardData{
						ConfigNum:  args.ConfigNum,
						ShardNum:   args.ShardNum,
						Data:       replyCopy.Data,
						MsgIndexes: replyCopy.MsgIndexes,
					}
					kv.mu.Unlock()
					_, _, isLeader := kv.rf.Start(mergeArgs)
					if !isLeader {
						break
					}
				} else {
					kv.mu.Unlock()
				}
			}
		}
	}
}

// StartServer() must return quickly, so it should start goroutines for any long-running work.
func StartServer(servers []*labrpc.ClientEnd, me int, persister *raft.Persister, maxraftstate int, gid int, masters []*labrpc.ClientEnd, make_end func(string) *labrpc.ClientEnd) *ShardKV {
	// call labgob.Register on structures you want
	// Go's RPC library to marshall/unmarshall.
	labgob.Register(Op{})
	kv := new(ShardKV)
	kv.me = me
	kv.maxraftstate = maxraftstate
	kv.make_end = make_end
	kv.gid = gid
	kv.masters = masters
	kv.persister = persister

	// Use something like this to talk to the shardmaster:
	kv.mck = shardmaster.MakeClerk(kv.masters)

	kv.applyCh = make(chan raft.ApplyMsg)
	kv.stopCh = make(chan struct{})
	kv.rf = raft.Make(servers, me, persister, kv.applyCh, kv.gid)

	// You may need initialization code here.
	kv.data = [shardmaster.NShards]map[string]string{}
	for i := range kv.data {
		kv.data[i] = make(map[string]string)
	}
	kv.lastMsgIdx = [shardmaster.NShards]map[int64]int64{}
	for i := range kv.lastMsgIdx {
		kv.lastMsgIdx[i] = make(map[int64]int64)
	}
	kv.waitShardIds = make(map[int]bool)
	kv.historyShards = make(map[int]map[int]MergeShardData)
	config := shardmaster.Config{
		Num:    0,
		Shards: [shardmaster.NShards]int{},
		Groups: map[int][]string{},
	}
	kv.config = config
	kv.oldConfig = config
	kv.readSnapShotData(kv.persister.ReadSnapshot())

	kv.notifyCh = make(map[int64]chan NotifyMsg)
	kv.pullConfigTimer = time.NewTimer(PullConfigInterval)
	kv.pullShardsTimer = time.NewTimer(PullShardsInterval)

	go kv.waitApplyCh()
	go kv.pullConfig()
	go kv.pullShards()

	return kv
}
