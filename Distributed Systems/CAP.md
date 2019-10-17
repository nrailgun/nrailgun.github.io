*Brewer's conjecture and the feasibility of consistent, available, partition-tolerant web services* 一文提出了著名的 **CAP 不可能定理**。

> It's impossible in the asynchrous network model to implement a read / write data object that guarantee the following properties:
>
> - Availability
> - Atomic consistency
>
> in all fair executions (including those in which messages are lost).

实际上 *messages are lost* 是指网络分割导致不可达的情况。论文通过反证法证明了 CAP 不可能定理，基本思路相对简单，但是在 2002 年才被提出。

假定两个节点 $\{ G_1, G_2 \}$ 之间被完全分割，消息完全不可达，写操作发生在 $G_1$，随后在 $G_2$ 的操作不可能读取到最新的值。证毕。

