package shardmaster

import (
	"labgob"
	"labrpc"
	"raft"
	"sort"
	"sync"
	"time"
)

const WaitCmdTimeOut = time.Millisecond * 500

type NotifyMsg struct {
	Err         Err
	WrongLeader bool
	Config      Config
}

type ShardMaster struct {
	mu      sync.Mutex
	me      int
	rf      *raft.Raft
	applyCh chan raft.ApplyMsg
	stopCh  chan struct{}

	// Your data here.
	msgNotify   map[int64]chan NotifyMsg
	lastApplies map[int64]int64 // last apply join/leave/move msg
	configs     []Config        // indexed by config num
}

type Op struct {
	// Your data here.
	MsgId    int64
	ReqId    int64
	Args     interface{}
	Method   string
	ClientId int64
}

func (sm *ShardMaster) Join(args *JoinArgs, reply *JoinReply) {
	// Your code here.
	res := sm.runCmd("Join", args.MsgId, args.ClientId, *args)
	reply.Err, reply.WrongLeader = res.Err, res.WrongLeader
}

func (sm *ShardMaster) Leave(args *LeaveArgs, reply *LeaveReply) {
	// Your code here.
	res := sm.runCmd("Leave", args.MsgId, args.ClientId, *args)
	reply.Err, reply.WrongLeader = res.Err, res.WrongLeader
}

func (sm *ShardMaster) Move(args *MoveArgs, reply *MoveReply) {
	// Your code here.
	res := sm.runCmd("Move", args.MsgId, args.ClientId, *args)
	reply.Err, reply.WrongLeader = res.Err, res.WrongLeader
}

func (sm *ShardMaster) Query(args *QueryArgs, reply *QueryReply) {
	// Your code here.
	sm.mu.Lock()
	if args.Num > 0 && args.Num < len(sm.configs) {
		reply.Err = OK
		reply.WrongLeader = false
		reply.Config = sm.getConfigByIndex(args.Num)
		sm.mu.Unlock()
		return
	}
	sm.mu.Unlock()
	res := sm.runCmd("Query", args.MsgId, args.ClientId, *args)
	reply.Err = res.Err
	reply.WrongLeader = res.WrongLeader
	reply.Config = res.Config
}

// 平衡 shard 和 group
func (sm *ShardMaster) adjustConfig(config *Config) {
	if len(config.Groups) == 0 {
		config.Shards = [NShards]int{}
	} else if len(config.Groups) == 1 {
		// all shards -> one group
		for k := range config.Groups {
			for i := range config.Shards {
				config.Shards[i] = k
			}
		}
	} else if len(config.Groups) <= NShards {
		avg := NShards / len(config.Groups)
		// 每个 gid 分 avg 个 shard
		otherShardsCount := NShards - avg*len(config.Groups)
		needLoop := false
		lastGid := 0
	LOOP:
		var keys []int
		for k := range config.Groups {
			keys = append(keys, k)
		}
		sort.Ints(keys)
		for _, gid := range keys {
			lastGid = gid
			count := 0
			// 先 count 已有的: 每个 gid 对应的 shard 数量
			for _, val := range config.Shards {
				if val == gid {
					count += 1
				}
			}
			// 判断是否需要改变
			if count == avg {
				continue
			}
			if count > avg && otherShardsCount >= 0 {
				// 减到 othersShardsCount 为 0
				// 若还 count > avg, set to 0
				c := 0
				for i, val := range config.Shards {
					if val == gid {
						if c == avg + otherShardsCount {
							// otherShardsCount 可能是 0	
							config.Shards[i] = 0
						} else if c == avg {
							// otherShardsCount 必不是 0
							otherShardsCount -= 1
						} else {
							c += 1
						}
					}
				}
			} else {
				// count < avg, 此时有可能没有位置
				for i, val := range config.Shards {
					if count == avg {
						break
					} else if count < avg && val == 0 {
						config.Shards[i] = gid
					}
				}
				if count < avg {
					needLoop = true
				}
			}
		}
		if needLoop {
			needLoop = false
			goto LOOP
		}
		// 可能每一个 gid 都 >= avg，但此时有空的 shard
		if lastGid != 0 {
			for i, val := range config.Shards {
				if val == 0 {
					config.Shards[i] = lastGid
				}
			}
		}
	} else {
		// len(config.Groups) > NShards
		// 每个 gid 最多一个 shard, 会有空余 gid
		gids := make(map[int]int)
		emptyShards := make([]int, 0, NShards)
		// 把 gid == 0 或者 gid 重复的 shard 放到 emptyShards
		for i, gid := range config.Shards {
			if gid == 0 {
				emptyShards = append(emptyShards, i)
				continue
			} else if _, ok := gids[gid]; ok {
				emptyShards = append(emptyShards, i)
				config.Shards[i] = 0
			} else {
				gids[gid] = 1
			}
		}
		n := 0
		if len(emptyShards) > 0 {
			var keys []int
			for k := range config.Groups {
				keys = append(keys, k)
			}
			sort.Ints(keys)
			for _, gid := range keys {
				if _, ok := gids[gid]; !ok {
					// 如果 Groups 中的 gid 未在 gids 中, 则用一个 shard 分配
					config.Shards[emptyShards[n]] = gid
					n += 1
				}
				// gid 太多 shard 不够用了
				if n >= len(emptyShards) {	
					break
				}
			}
		}
	}
}

// 创建新的 GID -> servers 映射, 重新平衡 shards
func (sm *ShardMaster) join(args JoinArgs) {
	config := sm.getConfigByIndex(-1)
	config.Num += 1
	for k, v := range args.Servers {
		config.Groups[k] = v
	}
	sm.adjustConfig(&config)
	sm.configs = append(sm.configs, config)
}

// 删除一些组, 将这些组的 shards 重新分配给其他组
func (sm *ShardMaster) leave(args LeaveArgs) {
	config := sm.getConfigByIndex(-1)
	config.Num += 1
	for _, gid := range args.GIDs { 
		delete(config.Groups, gid)
		for i, v := range config.Shards {
			if v == gid {
				config.Shards[i] = 0
			}
		}
	}
	sm.adjustConfig(&config)
	sm.configs = append(sm.configs, config)
}

// 配置一个组到对应 shard
func (sm *ShardMaster) move(args MoveArgs) {
	config := sm.getConfigByIndex(-1)
	config.Num += 1
	config.Shards[args.Shard] = args.GID
	sm.configs = append(sm.configs, config)
}

func (sm *ShardMaster) getConfigByIndex(idx int) Config {
	if idx < 0 || idx >= len(sm.configs) {
		return sm.configs[len(sm.configs)-1].Copy()
	} else {
		return sm.configs[idx].Copy()
	}
}

func (sm *ShardMaster) runCmd(method string, id int64, clientId int64, args interface{}) (res NotifyMsg) {
	op := Op{
		MsgId:    id,
		ReqId:    nrand(),
		Args:     args,
		Method:   method,
		ClientId: clientId,
	}
	res = sm.waitCmd(op)
	return
}

// 将 RPC 请求的 Command 通过 Raft 写入 Logentries, 等待 Command 执行完成返回结果
func (sm *ShardMaster) waitCmd(op Op) (res NotifyMsg) {
	_, _, isLeader := sm.rf.Start(op)	// 启动 raft
	if !isLeader {
		res.Err = ErrWrongLeader
		res.WrongLeader = true
		return
	}
	sm.mu.Lock()
	ch := make(chan NotifyMsg, 1)
	sm.msgNotify[op.ReqId] = ch
	sm.mu.Unlock()
	// 启动定时器
	t := time.NewTimer(WaitCmdTimeOut)
	defer t.Stop()
	select {
	case res = <-ch:	// 完成
		sm.removeCh(op.ReqId)
		return
	case <-t.C:			// 超时
		sm.removeCh(op.ReqId)
		res.WrongLeader = true
		res.Err = ErrTimeout
		return
	}
}

// the tester calls Kill() when a ShardMaster instance won't
// be needed again. you are not required to do anything
// in Kill(), but it might be convenient to (for example)
// turn off debug output from this instance.
func (sm *ShardMaster) Kill() {
	sm.rf.Kill()
	// Your code here, if desired.
	close(sm.stopCh)
}

// needed by shardkv tester
func (sm *ShardMaster) Raft() *raft.Raft {
	return sm.rf
}

func (sm *ShardMaster) removeCh(id int64) {
	sm.mu.Lock()
	defer sm.mu.Unlock()
	delete(sm.msgNotify, id)
}

func (sm *ShardMaster) apply() {
	for {
		select {
		case <-sm.stopCh:
			return
		case msg := <-sm.applyCh:
			if !msg.CommandValid {
				continue
			}
			op := msg.Command.(Op)
			sm.mu.Lock()
			isRepeated := sm.isRepeated(op.ClientId, op.MsgId)
			if !isRepeated {
				switch op.Method {
				case "Join":
					sm.join(op.Args.(JoinArgs))
				case "Leave":
					sm.leave(op.Args.(LeaveArgs))
				case "Move":
					sm.move(op.Args.(MoveArgs))
				case "Query":
				default:
					panic("unknown method")
				}
			}
			res := NotifyMsg{
				Err:         OK,
				WrongLeader: false,
			}
			if op.Method == "Query" {
				res.Config = sm.getConfigByIndex(op.Args.(QueryArgs).Num)
			} else {
				sm.lastApplies[op.ClientId] = op.MsgId
			}
			if ch, ok := sm.msgNotify[op.ReqId]; ok {
				ch <- res
			}
			sm.mu.Unlock()
		}
	}
}

func (sm *ShardMaster) isRepeated(clientId int64, id int64) bool {
	if val, ok := sm.lastApplies[clientId]; ok {
		return val == id
	}
	return false
}

// servers[] contains the ports of the set of
// servers that will cooperate via Paxos to
// form the fault-tolerant shardmaster service.
// me is the index of the current server in servers[].
func StartServer(servers []*labrpc.ClientEnd, me int, persister *raft.Persister) *ShardMaster {
	labgob.Register(Op{})
	sm := new(ShardMaster)
	sm.me = me

	sm.configs = make([]Config, 1)
	sm.configs[0].Groups = map[int][]string{}
	sm.applyCh = make(chan raft.ApplyMsg, 100)
	sm.stopCh = make(chan struct{})
	sm.rf = raft.Make(servers, me, persister, sm.applyCh)

	sm.lastApplies = make(map[int64]int64)
	sm.msgNotify = make(map[int64]chan NotifyMsg)

	// Your code here.
	go sm.apply()

	return sm
}
