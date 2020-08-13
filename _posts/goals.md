# Learning Goals

- Programming Languages
    - [x] *The Go Progamming Language*
    - [x] *The Lua Programming Language*
    - [x] *The Rust Programming Language*
    - [x] *Effective Rust*
    - [x] *Modern C++ Tutorial*
- Tools
    - [x] MongoDb
    - [x] Redis
    - [x] Jenkins
    - [x] Nginx
    - [x] *W3C SQL Tutorial*
    - [x] *Docker Quickstart*
    - [x] *K8S Tutorial: Learn K8S Basics*
    - [x] *W3C Awk Tutorial*
    - [x] *Action in K8S*: CH 1~11
- Algorithms
    - [x] *数据结构与算法分析：C++ 语言描述*
    - [x] *STL 源码剖析*
    - [x] bloom filter
    - [x] consistent hashing
    - [ ] *Introduction To Algorithms*
      - [ ] CH 1
- OS and Distributed Systems
    - [x] 2PC
    - [x] Gossip
    - [x] Lamport Clock
    - [x] Paxos
    - [x] Raft
    - [x] MIT 6.824
      - [x] map reduce
      - [x] raft
      - [x] kv store
    - [x] *Software Architecture Patterns: Understanding Common Architecture Patterns and When to Use Them*
    - [x] *Designing Distributed Systems: PATTERNS AND PARADIGMS FOR SCALABLE, RELIABLE SERVICES*
    - [ ] MIT 6.828
    - [ ] *PC Assembly Language*
- A Little of Everything
    - [x] SSL / TLS
    - [ ] 股票

# Tricks

- 处理全部异常（不可恢复的异常要保证正确料理处理器后事）。
- 状态转移所期望的行为可能丢失吗？可能发生意外的行为吗？理想上，应该明确功能的假定条件和不变式；但现实中，它们往往随着迭代而被打破。
- 由于假定条件和不变式经常被打破，需要提前考虑线上出错数据要如何修正，尽量选取数据易修正的方案。
- 函数要注意可能的重入，与意外上下文错误（如失误的重复调用）。即使没有发生协程调度，也要小心意外的上下文改变（例如时间）。
- 命名是件需要认真对待的事情。

  - 一种事物应该只拥有一个命名，一个命名应该只对应一种事物。
  - 避免使用实际上没有任何含义的命名，除非作用域完全局部化且代码很简单。
- 尽量避免使用数字开头命名文件，否则可能与模块命名不一致，或者在反射时发生麻烦。
  - 如果存在多种不同的整型标识符，很可能错误传递导致悲剧。使不同标识符的类型/变量命名显著不同（例如不要使用 UId / UserId）。即使使用整型，也尽量定义别名，方便编译器 / 解释器检查。
- 代码要调用尽量避免循环调用，尤其是在回调中。很可能发生难以估计的潜在副作用。
- 有些需求直接实现比较棘手，可以换一种思路用人力处理问题。
- 不要设计无法校验合法性的句柄。典型的例子是悬垂指针，或者是无法知晓定时器是否已经触发的定时器编号。
- 缓存记得定时逐出内存。

# Thoughts

- 你可以看穿历史的进程，可你却跳不出。
- 在行动之前，注意信息收集，切勿想当然。一个行业或者领域可能业务开展很不理想，即使当前在你的地区很不错，在另一个地区也不一定成立。当信息收集不完善，决策就变成了纯赌博（虽然完全收集是不可能的）。
- 资本市场价格取决于供需关系，而盈利则需要考虑成本。行业某些畸形发展（价格战，技术战）导致成本提高盈利能力降低，进而导致资本撤离。对于人也是同理，你在市场出卖劳务的价格，不取决于能力门槛，而取决于市场需求和投资热情。
- 物品的价值对于不同的用户是不同的，避免按照自身盲目揣测。例子便是中大毕业典礼门票和网易游戏新春礼包。
- 如果有人质疑你的软实力，不要顺着其思路走，直接否认。

# Defered Learning Goals

Video Game Developing
- [x] Frameworks
  - [x] Mobile Server
  - [x] Unity
- [x] Pathfinding
  - [x] Detour
  - [x] Mapper
  - [x] ORCA
  - [ ] Recast
- [ ] Game Physics
  - [x] Physics for Game Programmers
  - [x] Physics for Game Developers
  - [x] Collision3D
  - [x] Game Physics Engine Development
  - [x] Game Physics 2nd Edition
  - [x] Box2D Quickstart
  - [ ] *Realtime Collision Detection*
  - [ ] *Fast Contact Reduction for Dynamics Simulation, Game Programming Gems 4*
- [ ] GDC Works
