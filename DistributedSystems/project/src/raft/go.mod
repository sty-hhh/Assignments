module raft

go 1.19

require (
	labgob v0.0.0
	labrpc v0.0.0
)

replace (
	labgob => ../labgob
	labrpc => ../labrpc
)
