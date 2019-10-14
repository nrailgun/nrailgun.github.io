## Redis Revisited

## Cluster

集群相关消息处理有两个端口：

1. 集群内部：`main` 启动过程中 `initServer` 调用`clusterInit` 初始化集群，`clusterInit` 会注册 `clusterReadHandler` 用于 `epoll` 读事件用于集群通信。`clusterReadHandler`读取完整包后调用 `clusterProcessPacket`。
2. 集群外部：客户端发送 `'CLUSTER *'` 指令管理集群，命令和普通命令一样通过 `processCommand`，调用 `clusterCommand` 处理。

节点会间歇性在 `clusterCron` 中通过 `PING / PONG` 消息交换集群布局（layout）。

当集群节点布局发生变化时，节点不会立刻使用 **direct mailing gossip** 的方式通知所有节点，而是采用 **anti-entropy gossip** 的方式随机通知集群中节点。Anti-entropy 无法完全同步的时间上限，但是数学期望可期，且最终将完全同步（eventually consistent）。

**TODO**: 

1. 在 sharding slot 发生变化时，同步的行为似乎有所不同。
2. `currentEpoch` & `configEpoch` 是什么？

### Replication

Primary / replica 模式有两个好处：

- 读写分离
- 相当程度的容灾

Redis 的 replication 可以视为 direct mailing gossip 的一个变种（可能并不准确？）。与强一致的 Etcd / LogCabin 不同，为了减少 latency，Redis 不会等待复制完成就回报客户端操作完成。如果此时突然宕机或 replica 突然被 read，会出现不一致。注意在发生 failover 的情况下，Redis 甚至不能保证 sequential consistency。

>  Redis Cluster is not able to guarantee **strong consistency**. In practical terms this means that under certain conditions it is possible that Redis Cluster **will lose writes that were acknowledged** by the system to the client. 

## Sharding

**TODO**

### Sentinel

Primary 节点可能失败，需要 sentinel failover 将 replica promote 为 primary。