module kvraft

go 1.19

require (
	labgob v0.0.0
	labrpc v0.0.0
	models v0.0.0
	porcupine v0.0.0
	raft v0.0.0
	shardmaster v0.0.0
)

replace (
	labgob => ../labgob
	labrpc => ../labrpc
	models => ../models
	porcupine => ../porcupine
	raft => ../raft
	shardmaster => ../shardmaster
)
