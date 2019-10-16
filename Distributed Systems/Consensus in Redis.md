## Redis Revisited

## Cluster

集群相关消息处理有两个端口：

1. 集群内部：`main` 启动过程中 `initServer` 调用`clusterInit` 初始化集群，`clusterInit` 会注册 `clusterReadHandler` 用于 `epoll` 读事件用于集群通信。`clusterReadHandler`读取完整包后调用 `clusterProcessPacket`。
2. 集群外部：客户端发送 `'CLUSTER *'` 指令管理集群，命令和普通命令一样通过 `processCommand`，调用 `clusterCommand` 处理。

节点会间歇性在 `clusterCron` 中通过 `PING / PONG` 消息交换集群布局（layout）。

当集群节点布局发生变化时，节点不会立刻使用 **direct mailing gossip** 的方式通知所有节点，而是采用 **anti-entropy gossip** 的方式随机通知集群中节点。Anti-entropy 无法完全同步的时间上限，但是数学期望可期，且最终将完全同步（eventually consistent）。

**TODO**:

1. sharding
2. 在 sharding slot 发生变化时，同步的行为似乎有所不同。
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

Redis sentinel 为了效率，并不会实时地询问其他节点的意见，而是间歇性地去检查（部分节点）并存储集群情况，当需要时以之前的结果为准，但不一定准确。这样的好处是集群通信压力会小一些，但是会导致一些误判。考虑到错误发起主从切换或略微推迟主从切换并不会导致太过于严重的后果，所以小概率的误判可以接受。如果你认为主从切换导致的潜在丢失写的后果不可接受，你不该选用 redis。

Sentinel 需要特殊处理 partition 导致的节点自以为是 master 的脑裂问题，因为 sentinel 既不是 paxos 那样一次性的 agreement，也不是像 raft 那样状态明确的强一致，所以无法简单通过一个 term 来推定 master 合法性。Redis 没有明确的理论模型，很难建立清晰的边界和严格的不变式，也很难明确状态是 disaster 还是 error（见 2PC 论文）。

由于 redis 没有使用稳定时钟，所以 redis sentinel 会定期检查时间回流和突进，如果发现异常，标记为 TILT，不再参与工作。Antirez 解释 redis 之所以不使用稳定时钟：

1. 稳定时钟需要在某些平台不可用；
2. 语义与 `EXPIRE` 的实现有冲突。

G17 的外服和内服都跑着 NTP 服务，理论上很可能出现类似的错误。

**TODO**

1. sentinel 节点是如何认知 layout 的？如果 layout 认知不正确（比如 3 个旧节点不认知 2 个旧节点），是否会导致 sentinel leader 脑裂进而导致 promote 多个 replica，最终导致 redis 脑裂？

