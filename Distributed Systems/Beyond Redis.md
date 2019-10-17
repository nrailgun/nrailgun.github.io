## INTRO

> A system is *distributed* if **the message transmission delay is not negligible** compared to the time between events in a single process.

为何需要设计分布式系统？

1. 单机的存储与算力无力支撑问题。
2. 计算机集群比超级计算机廉价（后者成本至少数亿美元）。

分布式系统主要分为两类，**分布式存储**和**分布式计算**。本文主要讨论分布式存储，特别是一致性问题。分布式存储的设计**目标**：

- **一致性**
  - 强一致
  - 弱一致
  - 顺序一致
  - 最终一致
- **可用性**
- **网络分裂容忍**
- 可拓展性
- 性能
  - 延迟
  - 吞吐量

设计实现分布式系统面临何种**困难**？

- 节点崩溃概率增加

- 通信
  - 通信延迟
  - 通信负载
- **难以证明与实现**
  - 形式化方法的内在缺陷
  - **诸多失败工程的前车之鉴**

## Map Reduce / GFS / Bigtable

分布式系统的研究可以回溯到 20 世纪 80 年代，但是实际的工程应用到 21 世纪初才由 Google 领头开展。Jeff Dean 在分布式计算领域发表了 3 篇著名论文：

- *MapReduce: Simplied Data Processing on Large Clusters*
- *The Google File System*
- *Bigtable: A Distributed Storage System for Structured Data*

实际上这三篇论文更多的是一种工程意义上的指导，也点明了实现了分布式系统需要考虑的问题，如，时钟同步，强一致性存储、可靠通信，和可靠存储等。论文工程性较强，有兴趣同学自行阅读论文。

Map reduce 是一种典型的函数式编程思想：拆分问题，合并答案。Jeff 把一个问题拆分成多个给多个 mapper 处理，reducer 汇总 mappers 的输出。很不幸并不是所有的问题都能有如同 word count 一样简单的拆分方法。

![Map Reduce Idea](D:/Downloads/mapreduce.png)

单机的存储存在一些问题：

- 即使是内核也无法保证存储的写入，因为最终决定权在于硬件，很难完全保证。RAID 只能减轻问题。
- 即使保证存储的安全，单节点的可用性也是一个问题。

Google 为了解决这个问题，设计了分布式文件系统 GFS 和 Bigtable，用于存储非结构化和结构化数据。其中间组件 Chubby 使用了 Paxos 的某个变种。

![GFS Arch](Behind Redis.assets/1571299166818.png)

## CAP Thorem

要解决一个现实需求，需要先抽象问题；要解决一个抽象问题，需要知道方案的边界在哪里。*Brewer's conjecture and the feasibility of consistent, available, partition-tolerant web services* 一文提出了著名的 **CAP 不可能定理**，简单而言：

(At most) 2 of 3 properties

- (Strong) **c**onsistency: Every read receives the most recent write or an error.
- **A**vailability:  Every request receives a (non-error) response, without the guarantee that it contains the most recent write.
- **P**artition tolerance:  The system continues to operate despite an arbitrary number of messages being dropped (or delayed) by the network between nodes.

can be satisfied simultaneously.

论文通过反证法证明了 CAP 不可能定理，基本思路相对简单，但是在 2002 年才被提出。

> It's impossible in the asynchrous network model to implement a read / write data object that guarantee the following properties:
>
> - Availability
> - Atomic consistency
>
> in all fair executions (including those in which messages are lost).

实际上 *messages are lost* 是指网络分割导致不可达的情况。假定两个节点 $\{ G_1, G_2 \}$ 之间被完全分割，消息完全不可达，写操作发生在 $G_1$，随后在 $G_2$ 的操作不可能读取到最新的值。因此不可能存在同时满足 CAP 性质的系统，证毕。

## Lamport Clock

> In a distributed system it's sometimes impossible to say that one of the 2 events occurred first.

计算机廉价时钟无法精确计时，是分布式系统面临的第一个挑战。由于成本制约，分布式系统不可能使用成本高达数百万美元的精确计时器。论文 *Time, Clocks, and the Ordering of Events in a Distributed System* 发表于 1978 年，作者是著名的 Leslie Lamport。

### The Partial Ordering

We assume that the system is composed of a collection of processes. Each process consists of a sequence of events.

*Definition*. The "**happened before**" relation "$\to$" on the set of events of a system is the smallest relation satisfying the following 3 conditions:

1. If $a$ and $b$ are events in the same process, and $a$ comes before $b$, then $a \to b$.
2. If $a$ is the sending of a message by one process and $b$ is the receipt of the same message by another process, then $a \to b$.
3. if $a \to b$ and $b \to c$, then $a \to c$.

Two events $a$ and $b$ are said to be **concurrent** if $a \not \to b$ and $b \not \to a$.

### Logical Clocks

We define a clock $C_i$ for each process $P_i$ to be a function which assigns a number $C_i\left(a\right)$ to any event $a$ in that process. The entire system of clocks is represented by the function $C$ which assigns to any event $b$ the number $C\left(b\right)$. where $C\left(b\right)=C_j\left(b\right)$ if b is an event in process $P_j$.

**Clock Condition**. For any events $a$, $b$: if $a \to b$, then $C\left(a\right) \lt C\left(b\right)$.

Clock Condition is satisfied if the following 2 conditions hold.

- **C1**​. If $a$ and $b$ are events in process $P_i$, and $a$ comes before $b$, then $C_i\left(a\right) < C_i\left(b\right)$.
- **C2**. If $a$ is the sending of a message by process $P_i$, and $b$ is the receipt of that message by process $P_j$, then $C_i\left(a\right) < C_j\left(b\right)$.

To guarantee that the system of clocks satisfies the Clock Condition, we will insure that satisfies conditions C1 and C2. **To meet C1 and C2, implementation rules IR1 and IR2 must be obeyed**.

- **IR1**. Each process $P_i$ increments $C_i$ between any 2 successive events.

- **IR2**.
  - If event $a$ is the sending of a message $m$ by process $P_i$, then the message contains a timestamp   $T_m = C_i(a)$.

  - Upon receiveing a message $m$, process $P_j$ sets $C_j$ greater than or equal to its present value greater than $T_m$.

### Ordering the Events Totally

We define a relation $\Rightarrow$ as follows: if $a$ is an event is process $P_i$ and b is an event in process $P_j$, them $a \Rightarrow b$ iff either

1. $C_i(a) \lt C_j(b)$

2. $C_i(a) = C_j(b)$ and $P_i \lt P_j$.

It's easy to see that this defines a total ordering and that the Clock Condition implies that if $a \to b$ then $a \Rightarrow b$. Being able to totally order the events can be very userful in implementing a distributed system.

We wish to find an algorithm for granting the resource to a process which satisifies the following 3 conditions:

1. **GC1**. A process which has been granted the resource must release it before it can be granted to an other process.
2. **GC2**. Different requests for the resource must be granted in the order in which they are made.
3. **GC3**. If every process which is granted the resource eventually releases it, then every request is eventually granted.

To solve the problem, we implement a system of clocks with rules IR1 and IR2, and use them to define a total ordering $\Rightarrow$ of all events. To simplify the problem, we make a assumption that messages tranlations are ordered and repliable (which can be easily satisfied by TCP).

**The algorithm is then defined by the following 5 rules**.

1. To request the resource, process $P_i$ sends the message *request resource* $(P_i, T_m)$ to **every other** process, and puts that message on its request queue, where $T_m$ is the timestamp of the message.
2. When  process $P_j$ receives the message *request resource* $(P_i, T_m)$, it places it on ties request queue and sends a timestamped acknowledge message to $P_i$.
3. To release the resource, process $P_i$ removes any *request resource* $(P_i, T_m)$ message from its request queue and sends a (timestamped) *release resource* to every other process.
4. When process $P_j$ receives a *releases resource* message, it removes any *request resource* $(P_i, T_m)$ message from its request queue.
5. Process $P_i$ is granted the resource when the following 2 conditions are satisified:
   1. There is a *request resource* $(P_i, T_m)$ in its request queue which is ordered before any other request in its queue which is ordered before any other request in its queue by the relation $\Rightarrow$.
   2. **$P_i$ has received a message from every other process timestamped later than $T_m$**.

It's easy to verify that the algorithm satifies condition GR1, GR2 and GR3.

This algorithm is distributed. However this algorithm requires the active participation of all the processes, and must know all the commands issued by other processes, so the failure of a single process will make the system unavailable. The problem of failure is a diffcult one. ***Without physical time, there is no way to distinguish a failed process from one which is just pausing between events***.

### Physical Clocks

Let $C_i(t)$ denotes the reading of the clock $C_i$ at physical time $t$. In order for the clock $C_i$ to be a true physical clock, we will assume that the following conditions are satisified:

- **PC1**. There exists a constant $\mathcal K \ll 1$ such that, for all $i$, $|\frac{d C_i(t)}{dt} - 1| \lt \mathcal K$.
- **PC2**. There exists a sufficiently small constant $\epsilon$ such that, For all $i$, $j$: $|C_i(t) - C_j(t)| \lt \epsilon$.

We now specialize IR1 and IR2 for our physical clocks as follows:

- **IR1'**. For each $i$, if $P_i$ does not receive a message at physical time $t$, then $C_i$ is differentiable at time $t$ and $\frac{dC_i(t)}{dt} > 0$.
- **IR2'**.
  - If $P_i$ sends a message $m$ at physical time $t$, then $m$ contains a timstamp $T_m = C_i(t)$.
  - Upon receiving a message $m$ at time $t'$, process $P_j$ sets $C_j(t')$ to $\max \left( C_j \left( t' \right), T_m + \mu_m \right)$.

where $\mu_m$ is the assumed minimum delay.

We now show that this **clock synchronizing algorithm** can be used to satisfy PC2 (**PC2 is not always satisfied as it was in logical clock case**). We assume that the system is described by a directed graph in which an arc from process $P_i$ to process $P_j$ represents a comminication line over which messages are sent. The **diameter** of the directed graph is the smallest number $d$ such that there is a path between any $P_i$ and $P_j$ having at most $d$ arcs.

**THEOREM**. Assume a strongly connected graph of processes with **diameter** $d$ which always obeys rules $IR1'$ and $IR2'$. Assume that for any message $m$, $\mu_m \le \mu$ for some constant $\mu$, and that for all $t \ge t_0$:

1. PC1 holds.

2. There are constant $\tau$ and $\xi$ such that every $\tau$ seconds a message which an unpredictable delay less than $\xi$ is sent over every arc. Then PC2 is satisfied with
   $$
   \epsilon \approx d(2 \mathcal K \tau + \xi)
   $$
    for all $t \gt t_0 + \tau d$, where the approximations assume $\mu + \xi \ll \tau$.

## 2 PC

2 PC 的论文 *Crash Recovery in a Distributed Data Storage System* 内容比较多，论文发表于 1979 年，具有很多非常前沿性的想法。不好意思这里写的比较潦草，很多很了不起的想法由于时间关系无法完整表达。

### Error and Disaster

首先界定系统的 event：

- Desired：无错误发生，满足用户的期望。
- Undesired
  - Expected / Error：预料之中的错误，如，网络异常、硬盘故障，或者对方节点宕机。
  - Unexpected / Disaster：预料之外的错误，如，程序**内部** bug，算法预期外的状态，CPU 错误。

一个**非拜占庭式**的系统，应该正确应对 expected undesired event，但是不应该处理 unexpected undesired event，此时系统的行为是完全未定义而不可估计的。

### Stable Storage

其次，论文提出了 stable storage 的概念。1979 年 RAID 论文尚未发表，此时论文已经提出了一种类似于 RAID 的存储方法：在两个故障独立的设备上进行存储，如果两者均存储成功，则认为存储成功。理由是两个设备同时故障的概率比较低。事实上，这也是日后 RAID 2 的基本思想。而对于 CPU / 硬盘误报正确的情况，文章认为这是一种 disaster，不予处理（事实上这种情况 GFS 也无力处理）。

文章对此方法的严格证明比较冗长，考虑到方法比较直观，这里不做赘述。

### The 2 PC

2 PC（两阶段提交，2 phase commit）是一种典型的“中心化副本控制”协议。 在该协议中，参与的节点分为两类：一个中心化协调者节点（coordinator）和 $N$ 个参与者节点（participant）。每个参与者节点即存储副本节点。

算法分为两个阶段：

1. Record the information necessary to do the writes in a set of intentions, without changing the data stored by the system. The last action taken in this phase is said to commit the transaction.
   Second, do the writes, actually changing the stored data.
2. Do the writes, actually changing the stored data.

算法的形式化描述比较冗长，考虑到思想比较直观，此处不再展开。2PC 协议的思想比较简单，可能是最容易理解的强一致性算法。缺点在于：

- 由于 2 PC 是中心化的，coordinator 的宕机会导致服务不可用。
- 2 PC 是阻塞的，在一次提交过程完成之前，不能进行其他操作。

## Gossip

Xerox 在 *Epidemic Algorithms for Replicated Database Maintenance* 中提出，他们使用 Gossip 算法实现了高可用分布式存储。Gossip 算法的特点是：高可用性（即使溃败到只有单节点也可用），较弱的（最终）一致性。

论文比较分析、比较了 Gossip 3 种不同的传播策略，包括：

- Direct mail：每个 update 都被**立刻**传播到**所有**的节点。这个方法时效性好，效率高，但是需要节点了解集群节点配置，单节点的失败会导致不一致。
- Anti-entroypy：每个节点**定期**随机选中一个其他节点，比较数据库内容并处理 update。该策略可靠性高，但是速度较慢，且需要大量的网络通信（比较数据库内容）。
- Rumor-mongering：当一个节点收到一个新的 update hot rumor，并随机选中一个节点并试图传播这个 update，如果有太多次传播时发现其他节点已经拥有了这个 update，那么这个 rumor 不再 hot，不再试图传播这个 update。该策略存在不能完全同步的风险。

论文主要通过实验比较了几种策略的几个关键指标：

- Residue：没有被 update 的节点数量。
- Traffic：网络消息数量。
- Delay：达到同步的时间。

由于实际的统计学证明比较困难，论文实际上采用了仿真实验的方式进行比较。具体数字因参数而异，有兴趣可自行翻阅论文。

Gossip 算法主要的问题在于，对于一致性的保证比较弱，有时候很难使用；此外，对于单节点失败能否同步某个 log 算法本身是没保证的。很难说 Gossip 算法是不是具有网络分割容忍。集群如果被分割为两个小集群，在这期间，两个小集群读自工作，完全不具备一致性，但是一旦网络被修复，最终将达成一致（eventual consistent）。

## Paxos

**Paxos** is a family of protocols for **solving consensus** in a network of unreliable processors. Paxos 的目标为：强一致（strongly consistent），网络分割最多导致不可用（partition tolerant），相当程度可用（almost available）。Paxos 的优点是理论上的纯净性，但是工程使用需要做诸多变种（如 GFS 中的 Chubby）。变种的证明又是另一个问题，实现困难。

Assume a collection of process that can propose values. A consensus algorithm **ensures that a single one among the proposed values is chosen**. If a value has been chosen, then processes should be able to learn that chosen value.

### Choosing a Value

Requiring different proposals have different numbers. How this is achieved depends on the implementation. 一个最简单的实现就是使用服务器编号 `host_id * MAX_SEQ_NUM + seq`。

The algorithm operates in the following 2 phases:

- **Phase 1**
  - A **proposer** selects a proposal number $n$ and sends a **prepare request** with number $n$ to a majority of **acceptor**s.
  - If an acceptor receives a prepare request with a number $n$ greater than any prepare request to which it already responded, then it responds with
    - a promise not to accept any more proposal numbered less $n$, and
    - the highest-numbered proposal (if any) that it has accepted.
- **Phase 2**
  - If the proposer receives a response to its prepare requests (numbered $n$) from a majority of acceptors, then it sends an **accept request** to **each** of those acceptors for a proposal numbered $n$ with a value $v$, where $v$ is the value of the highest-numbered proposalamong the responses, or is any value if the responses reported no proposals.
  - If an acceptor receives an accept request for a proposal numbered $n$, it **accepts** the proposal unless it has already responded to a **prepare request** having a number greater than $n$.

### Learning a Chosen Value

To learn that a value has been chosen, a **learner** must find out that a proposal has been accepted by a majority of acceptors.

1. The obvious algorithm is to have **each** acceptor, whenever it accepts a proposal, respond to **all** learners, sending them the proposal. The number responses could be large.
2. We can have the acceptors respond with their acceptances to a **distinguished learner**, which in turn informs the other learners when a value has been chosen. It is also less reliable, since the distinguished learner could fail.

The failure of an acceptor could make it impossible to know whether a majority had accepted a particular proposal. If a learner needs to know whether a value has been chosen, it can have a
proposer issue a proposal.

### Progress

It’s easy to construct a scenario in which two proposers each keep issuing a sequence of proposals with increasing numbers, none of which are ever chosen.

To **guarantee progress**, a **distinguished proposer** (some sort of leader) must be selected as the only one to try issuing proposals. The famous result of *F. L. P* implies that **a reliable algorithm for electing a proposer must use either randomness or real time**.

Lamport 这段话比较令人费解，我个人的理解是：Paxos 本身无法保证不会出现僵持的情况（*progress not ensured*），所以需要选一个 leader 来负责 propose value。使用 Paxos 来选择一个 leader 理论上也可能遇到僵持的情况，最简单的方法就是每次提 propose 一个 value 就随机 idle 一段时间。

## Raft

*In Search of an Understandable Consensus Algorithm* 提出了著名的 Raft 算法。**Raft** is a consensus algorithm for managing a replicated log. It produces a result equivalent to (multi-)Paxos (**strong consistency** and **partition tolerance**), but it's more understandable. It has several novel features: 

1. **strong leader**, 
2. **leader election**,
3. and **membership changes**.

### The Raft Consensus Algorithm

简单而言：

- 通过 leader 来代理所有的 log 同步，当 log 被*足够数量*的 follower 接收时，commit 这个 log 并执行。
- 后续Election 过程就是一个 lamport clock 的变种，请先阅读 lamport clock 的论文理解其思想。

注意足够数量（quorum）并不一定是过半数（majority）。下面是算法的 summary。

![1571301175387](Behind Redis.assets/1571301175387.png)

### Cluster Membership Changes

上文假定集群成员固定，实际上可能发生变化。最简单的方法是一个 2PC 过程，先暂停所有节点的服务并更新集群配置，随后再重启所有节点。Raft 认为这种方法可用性较低。

Raft 将新配置同步到 follower 节点，leader 所有的决议需要同时获得旧和新两个配置的半数节点统一才认为被 commit。一旦新配置被 commit，新 leader 可以保证不丢失新配置，此时添加新 log 去掉旧配置并等待其被提交。

## Redis Revisited

由于时间关系，redis 的代码只是大略扫过，如果讹误，还请斧正。关于 redis 的 metadata 的维护，大部分参考了 [Antirez 的 blog](http://antirez.com/news/62)。

### Cluster

集群相关消息处理有两个端口：

1. 集群内部：`main` 启动过程中 `initServer` 调用`clusterInit` 初始化集群，`clusterInit` 会注册 `clusterReadHandler` 用于 `epoll` 读事件用于集群通信。`clusterReadHandler`读取完整包后调用 `clusterProcessPacket`。
2. 集群外部：客户端发送 `'CLUSTER *'` 指令管理集群，命令和普通命令一样通过 `processCommand`，调用 `clusterCommand` 处理。

节点会间歇性在 `clusterCron` 中通过 `PING / PONG` 消息交换集群布局（layout）。

当集群节点布局发生变化时，节点不会立刻使用 **direct mailing gossip** 的方式通知所有节点，而是采用 **anti-entropy gossip** 的方式随机通知集群中节点。Anti-entropy 无法完全同步的时间上限，但是数学期望可期，且最终将完全同步（eventually consistent）。

**TODO**:

3. `currentEpoch` & `configEpoch` 是什么？

### Replication

Primary / replica 模式有两个好处：

- 读写分离
- 相当程度的容灾

Redis 的 replication 可以视为 direct mailing gossip 的一个变种（可能并不准确？）。与强一致的 Etcd / LogCabin 不同，为了减少 latency，Redis 不会等待复制完成就回报客户端操作完成。如果此时突然宕机或 replica 突然被 read，会出现不一致。注意在发生 failover 的情况下，Redis 甚至不能保证 sequential consistency。

>  Redis Cluster is not able to guarantee **strong consistency**. In practical terms this means that under certain conditions it is possible that Redis Cluster **will lose writes that were acknowledged** by the system to the client. 

`WAIT` 指令（quorum acknowledged writing）并不能保证强一致与不丢失，因为：

1. Redis 的存储本身不是严格意义可靠存储，定时存储之间也有时间空洞。
2. Redis 自身缺乏类似于 raft 的 *more up to date* 的识别机制，并不能保证 failover 中一定会选中那个 *more up to date* 的节点。

### Sentinel

Primary 节点可能失败，需要 sentinel failover 将 replica promote 为 primary。Redis 允许定义一个 `quorum`，表示允许多少 sentinel 认为 master 节点失效（即 `SDOWN`）。如果认为 master 故障的 sentinel 数量达到或超过了 `quorum`，即标记其为 `ODOWN`。但是 failover 需要获得 majority 的 sentinels 的认同。

Sentinel 要知道 majority 有多大，那么需要先知道集群的 layout。Sentinel 是如何了解 layout 的？因为 sentinel 实际上不支持删除 sentinel，故而新 sentinel 通过连接 master 可以很快了解 layout 和 majority。

> Removing a Sentinel is a bit more complex: **Sentinels never forget already seen Sentinels**, even if they are not reachable for a long time, since we **don't want to dynamically change the majority needed** to authorize a failover and the creation of a new configuration number.
>
> ...
>
> **Sentinels never forget about slaves of a given master**, even when they are unreachable for a long time. This is useful, because Sentinels should be able to correctly reconfigure a returning slave after a network partition or a failure event.

Redis sentinel 为了效率，并不会实时地询问其他节点的意见，而是间歇性地去检查（部分节点）并存储集群情况，当需要时以之前的结果为准，但不一定准确。这样的好处是集群通信压力会小一些，但是会导致一些误判。考虑到错误发起主从切换或略微推迟主从切换并不会导致太过于严重的后果，所以小概率的误判可以接受。

Sentinel 需要特殊处理 partition 导致的节点自以为是 master 的脑裂问题，因为 sentinel 既不是 paxos 那样一次性的 agreement，也不是像 raft 那样状态明确的强一致，所以无法简单通过一个 term 来推定 master 合法性。Redis 没有明确的理论模型，很难建立清晰的边界和严格的不变式，也很难明确状态是 disaster 还是 error（见 2PC 论文）。

由于 redis 没有使用稳定时钟，所以 redis sentinel 会定期检查时间回流和突进，如果发现异常，标记为 TILT，不再参与工作。Antirez 解释 redis 之所以不使用稳定时钟：

1. 稳定时钟需要在某些平台不可用；
2. 语义与 `EXPIRE` 的实现有冲突。

G17 的外服和内服都跑着 NTP 服务，理论上很可能出现类似的错误。

**TODO**

1. Sentinel 节点是如何认知 layout 的？如果 layout 认知不正确（比如 3 个旧节点不认知 2 个旧节点），是否会导致 sentinel leader 脑裂进而导致 promote 多个 replica，最终导致 redis 脑裂？我认为非强一致的情况下，sentinel add 的过程中会发生选出两个 leader 的情况，但是 redis 集群可以最终检测到并干掉其中一个。
2. Redis 是如何处理 sharding 的？

