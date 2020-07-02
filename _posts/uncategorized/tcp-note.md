

# TCP 笔记

## Header

TCP header 如下图所示：

1. seq num 用于处理乱序；
2. ack 用于处理丢包；
3. 滑动窗口；
4. flags（如 syn、ack 和 fin）。

![tcp header](https://nmap.org/book/images/hdr/MJB-IP-Header-800x576.png)

## ISN

ISN（initial sequence number）不能是固定数值，否则断开快速重连，第一次连接中 delay 的网络包在第二次网络包到达，会导致接收方 confused。所以 RFC 793 要求 4 微秒 ISN + 1，大概 4.55 小时为一个周期。理论上如果同一微秒内进行了两次连接，依旧会出现问题（虽然实际上即使是 loopback 也不可能 1 毫秒内达成两次 TCP 连接）。

Tcp segment 在网络的寿命为 MSL（maximum segment lifetime），只要 MSL < 4.55 小时，那么（合法构建的）packet 就不会和之前的 packet 混淆。

连接 close 的时候有一个 `TIME_WAIT` 的状态，也是为了处理这一问题。保证时间超过 $2 \times$ MSL（Linux 是 30s），让 delayed 的 packet 不会和新的 connection 混淆。当然接受挥手 ack 是 `TIMED_WAIT` 的另一个目的。

## 重传

### 超时重传

最简单就是超时重传。超时重传分两种，x 超时传 x，或者 x 超时传 x 后续所有。

### 快速重传

连续收到 3 次 ACK x，视为 x 丢失。同样分两种，传 x，或者传 x 后续所有。

### SACK

Selective Acknowledgment (SACK)。注意，用了 sack 也不能丢弃 timeout 机制，此外，接收方 sack 不能用于设置 ack。

![sack](https://coolshell.cn/wp-content/uploads/2014/05/tcp_sack_example-900x507.jpg)

### RTT

Smoothed Round Trip Time 是对 RTT 的平滑估计：
$$
\mathrm{SRTT} = \alpha \times \mathrm{SRTT} + (1 - \alpha) \times \mathrm{RTT}
$$
RTO (Retransmission Timeout) 估计：
$$
\mathrm{RTO} = \min \left[ \mathrm{UBOUND}, \max \left[ \mathrm{LBOUND},   \beta * \mathrm{SRTT} \right] \right]
$$

$\beta$ 是一个 1.3~2.0 之间的经验值。

但是 RTT 怎么计算呢？是用第一次发数据的时间和 ack 回来的时间做 RTT，还是用重传的时间和 ack 回来的时间做 RTT？

- ack 没回来，重传。如果你计算第一次发送和 ack 的时间，明显算大了。

- ack 回慢了，重传。但刚重传，之前 ack 回来了。如果你是算重传的时间和 ack 回来的时间的差，就会算短了。

![](https://coolshell.cn/wp-content/uploads/2014/05/Karn-Partridge-Algorithm.jpg)

Karn / Partridge Algorithm 直接忽略重传，不把重传的RTT做采样，一旦重传，RTO 翻倍。

Jacobson / Karels 算法用了一个神奇的经验公式：
$$
\mathrm{SRTT} = \mathrm{SRTT} + \alpha \left( \mathrm{RTT} – \mathrm{SRTT} \right) \\
\mathrm{DevRTT} = (1-\beta) \times \mathrm{DevRTT} + \beta \times \left| \mathrm{RTT} - \mathrm{SRTT} \right| \\
\mathrm{RTO} = \mu \times \mathrm{SRTT} + \partial \times \mathrm{DevRTT}
$$
Dev 是指 deviation 标准差。

### 滑动窗口

滑动窗口用于 flow control 控制发送速率。

如果窗口大小为 0，发送方会间歇性发送 zero window probe 来询问是否可发送了。

糊涂窗口：在窗口很小的情况下，用一个 tcp 头来投递数据，效率很差。

Nagle 算法用来解决糊涂窗口问题，必须

1. window size 或者 data size $>$ MSS，并且
2. 收到之前 packet 的 ack，

才会发送数据。在 delay 要求很高的情况下，该算法并不适用，用 `TCP_NODELAY` 来关闭。

## 拥塞控制

Flow control 只是协调连接双方，避免超载。Congestion handling 是根据整个网络的拥塞程度，做出适应。如果网络拥挤，那么 TCP 容易丢包，如果 TCP 一丢包就重传，那么拥挤问题就会更加严重（*嗯，看来 TCP 设计者和网络服务提供商似乎是利益同盟？*）。

**发送窗口的大小是接收方滑动窗口与发送方拥塞窗口的两者中较小值**。

### 慢启动

1. 连接建好的开始先初始化 cwnd = 1，表明可以传一个 MSS 大小的数据（Linux 3.0 初始化为 10 个 MSS）；
2. 每当收到一个 ACK cwnd++，呈线性上升；
3. 每当过了一个 RTT，cwnd = cwnd * 2，呈指数让升；
4. 还有一个 ssthresh（slow start threshold），当 cwnd >= ssthresh 时，进入“拥塞避免”。

如果网速很快的话，ACK 返回快，RTT 也短，那么慢启动过程会非常迅速。

### 拥塞避免

当 cwnd >= ssthresh 时，进入“拥塞避免”，控制增长速率，cwnd 大小呈线性增长。

1. 收到一个 ACK 时，cwnd = cwnd + 1 / cwnd；
2. 每过一个 RTT 时，cwnd = cwnd + 1。

### 拥塞状态

1. RTO 超时，重传数据包。
   1. sshresh = cwnd / 2；
   2. cwnd = 1；
   3. 进入慢启动。
2. 收到 3 个 dup ack，快速重传（Tcp Reno）。
   - sshthresh = cwnd / 2；
   - cwnd = cwnd / 2，折半窗口；
   - 进入快速恢复。

### 快速恢复

1. cwnd = sshthresh  + 3 * MSS （3 只 3 个 dup ack）；
2. 重传 dup ack 指定的数据包；
3. 如果再收到 dup ack，那么cwnd = cwnd + 1；
4. 如果收到了新 ack，那么，cwnd = sshthresh ，进入拥塞避免。

总而言之，拥塞控制的核心是找到一个合适的 cwnd，使得速度尽量快，又避免网络过度拥塞。各种各样的算法都是在经验法则下，试图尽快找到合适的 cwnd。由于实际的网络环境充满了各种不遵守规则的流氓协议，所以实际效果并不会完全符合预期。