package kvraft

import (
	"bytes"
	"labgob"
	"labrpc"
	"raft"
	"sync"
	"sync/atomic"
	"time"
)

const WaitCmdTimeOut = time.Millisecond * 500	

type Op struct {
	// Your definitions here.
	// Field names must start with capital letters,
	// otherwise RPC will break.
	MsgId    int64		// CommandArgs id (随机生成), 与 ClientId 一起判断 Command 是否重复 
	ReqId    int64		// NotifyMsg 索引 (随机生成), 映射对应 Command 的完成结果 (返回给 RPC)
	ClientId int64		// 客户端 id
	Key      string
	Value    string
	Method   string
}

type NotifyMsg struct {
	Err   Err
	Value string
}

type KVServer struct {
	mu      sync.Mutex
	me      int
	rf      *raft.Raft
	applyCh chan raft.ApplyMsg
	dead    int32 

	maxraftstate int // snapshot if log grows this big
	// Your definitions here.
	msgNotify   map[int64]chan NotifyMsg
	lastApplies map[int64]int64 // last apply put/append/delete msg
	data        map[string]string
	persister   *raft.Persister
}

// 返回 key 的 value, 没有返回 ErrNoKey
func (kv *KVServer) dataGet(key string) (err Err, val string) {
	if v, ok := kv.data[key]; ok {
		err = OK
		val = v
		return
	} else {
		err = ErrNoKey
		return
	}
}

// RPC: Get
func (kv *KVServer) Get(args *GetArgs, reply *GetReply) {
	// Your code here.
	_, isLeader := kv.rf.GetState()	// 获取当前 Term, 判断自己是否是 Leader
	if !isLeader {
		reply.Err = ErrWrongLeader
		return
	}
	op := Op{
		MsgId:    args.MsgId,
		ReqId:    nrand(),
		Key:      args.Key,
		Method:   "Get",
		ClientId: args.ClientId,
	}
	res := kv.waitCmd(op)
	reply.Err = res.Err
	reply.Value = res.Value
}

// RPC: PutAppend
func (kv *KVServer) PutAppend(args *PutAppendArgs, reply *PutAppendReply) {
	// Your code here.
	op := Op{
		MsgId:    args.MsgId,
		ReqId:    nrand(),
		Key:      args.Key,
		Value:    args.Value,
		Method:   args.Op,
		ClientId: args.ClientId,
	}
	reply.Err = kv.waitCmd(op).Err
}

// RPC: Delete
func (kv *KVServer) Delete(args *DeleteArgs, reply *DeleteReply) {
	op := Op{
		MsgId:    args.MsgId,
		ReqId:    nrand(),
		Key:      args.Key,
		Method:   "Delete",
		ClientId: args.ClientId,
	}
	reply.Err = kv.waitCmd(op).Err
}

// 不论 Command 执行完成/超时, 删除 id
func (kv *KVServer) removeCh(id int64) {
	kv.mu.Lock()
	delete(kv.msgNotify, id)
	kv.mu.Unlock()
}

// 将 RPC 请求的 Command 通过 Raft 写入 Logentries, 等待 Command 执行完成返回结果
func (kv *KVServer) waitCmd(op Op) (res NotifyMsg) {
	_, _, isLeader := kv.rf.Start(op)	// 启动 raft, 把 Command 写入 log
	if !isLeader {
		res.Err = ErrWrongLeader
		return
	}
	kv.mu.Lock()
	ch := make(chan NotifyMsg, 1)
	kv.msgNotify[op.ReqId] = ch
	kv.mu.Unlock()
	// 启动定时器: 等待 Command 
	t := time.NewTimer(WaitCmdTimeOut)
	defer t.Stop()
	select {
	case res = <-ch:	// Command 执行完成
		kv.removeCh(op.ReqId)
		return
	case <-t.C:		// Command 超时
		kv.removeCh(op.ReqId)
		res.Err = ErrTimeOut
		return
	}
}

//
// the tester calls Kill() when a KVServer instance won't
// be needed again. for your convenience, we supply
// code to set rf.dead (without needing a lock),
// and a killed() method to test rf.dead in
// long-running loops. you can also add your own
// code to Kill(). you're not required to do anything
// about this, but it may be convenient (for example)
// to suppress debug output from a Kill()ed instance.
//
func (kv *KVServer) Kill() {
	atomic.StoreInt32(&kv.dead, 1)
	kv.rf.Kill()
}

func (kv *KVServer) killed() bool {
	z := atomic.LoadInt32(&kv.dead)
	return z == 1
}

// 判断 Command 是否重复执行
func (kv *KVServer) isRepeated(clientId int64, id int64) bool {
	if val, ok := kv.lastApplies[clientId]; ok {
		return val == id
	}
	return false
}

func (kv *KVServer) waitApplyCh() {
	for !kv.killed() {
		msg := <-kv.applyCh		// 等待 Command msg 
		// rf.lastApplied < rf.lastSnapshotIndex, 需要读取snapshot
		if !msg.CommandValid {	
			kv.mu.Lock()
			kv.readPersist(kv.persister.ReadSnapshot())
			kv.mu.Unlock()
			continue
		}
		// Get/Put/Append/Delete
		kv.mu.Lock()
		op := msg.Command.(Op)
		isRepeated := kv.isRepeated(op.ClientId, op.MsgId)
		// 对 data 执行 Command
		switch op.Method {
		case "Get":
		case "Put":
			if !isRepeated {
				kv.data[op.Key] = op.Value
				kv.lastApplies[op.ClientId] = op.MsgId
			}
		case "Append":
			if !isRepeated {
				_, v := kv.dataGet(op.Key)
				kv.data[op.Key] = v + op.Value
				kv.lastApplies[op.ClientId] = op.MsgId
			}
		case "Delete":
			if !isRepeated {
				delete(kv.data, op.Key)
				kv.lastApplies[op.ClientId] = op.MsgId
			}
		default:
			panic("unknown method")
		}
		kv.saveSnapshot(msg.CommandIndex)
		// 向通道 ch 通知操作成功, 对 Get 命令返回 Value
		if ch, ok := kv.msgNotify[op.ReqId]; ok {
			_, v := kv.dataGet(op.Key)
			ch <- NotifyMsg{
				Err:   OK,
				Value: v,
			}
		}
		kv.mu.Unlock()
	}
}

// 保存 logIndex 之前的 data
func (kv *KVServer) saveSnapshot(logIndex int) {
	if kv.maxraftstate == -1 || kv.persister.RaftStateSize() < kv.maxraftstate {
		return
	}
	data := kv.genSnapshotData()
	kv.rf.Snapshot(logIndex, data)	
}

func (kv *KVServer) genSnapshotData() []byte {
	w := new(bytes.Buffer)
	e := labgob.NewEncoder(w)
	e.Encode(kv.data)
	e.Encode(kv.lastApplies)
	data := w.Bytes()
	return data
}

func (kv *KVServer) readPersist(data []byte) {
	if data == nil || len(data) < 1 { 
		return
	}
	r := bytes.NewBuffer(data)
	d := labgob.NewDecoder(r)
	var kvData map[string]string
	var lastApplies map[int64]int64
	if d.Decode(&kvData) != nil ||
		d.Decode(&lastApplies) != nil {
	} else {
		kv.data = kvData
		kv.lastApplies = lastApplies
	}
}

//
// servers[] contains the ports of the set of
// servers that will cooperate via Raft to
// form the fault-tolerant key/value service.
// me is the index of the current server in servers[].
// the k/v server should store snapshots through the underlying Raft
// implementation, which should call persister.SaveStateAndSnapshot() to
// atomically save the Raft state along with the snapshot.
// the k/v server should snapshot when Raft's saved state exceeds maxraftstate bytes,
// in order to allow Raft to garbage-collect its log. if maxraftstate is -1,
// you don't need to snapshot.
// StartKVServer() must return quickly, so it should start goroutines
// for any long-running work.
//
func StartKVServer(servers []*labrpc.ClientEnd, me int, persister *raft.Persister, maxraftstate int) *KVServer {
	// call labgob.Register on structures you want
	// Go's RPC library to marshall/unmarshall.
	labgob.Register(Op{})
	kv := new(KVServer)
	kv.me = me
	kv.applyCh = make(chan raft.ApplyMsg)
	kv.rf = raft.Make(servers, me, persister, kv.applyCh)
	kv.maxraftstate = maxraftstate
	kv.msgNotify = make(map[int64]chan NotifyMsg)
	kv.lastApplies = make(map[int64]int64)
	kv.persister = persister
	kv.data = make(map[string]string)
	kv.readPersist(kv.persister.ReadSnapshot())
	
	// 执行 LogEntries 中的 Command
	go kv.waitApplyCh()

	return kv
}