---
layout: post
title: "Linux Debug Tools"
categories: tools
date: 2020-10-03 00:00:00
---

# tcpdump

REFs:

1. [超详细的网络抓包神器 tcpdump 使用指南](https://juejin.im/post/6844904084168769549)
2. [Tcpdump Examples](https://hackertarget.com/tcpdump-examples/)

---

常用参数：

```bash
tcpdump -i eth0 -nn -s0 -v tcp port 80
```

- -i: 捕获设备
- -nn:
- -s*x*：显示 *x* 长度，如果 *x* = 0 显示全部。
- -v, -vv, -vvv: verbose
- -A: display in ASC-II
- -X: display in hex

---

capture specific `host` / `src` / `host` only:

```bash
 tcpdump -i eth0 host 10.10.1.1
```

---

line buffer mode

```bash
tcpdump -i eth0 -s0 -l port 80 | grep 'Server:'
```

# strace

```bash
strace -i -t ls
```

- -i: print instruction pointer
- -t: print timestamp
- -T show time spent in syscall

similar tools:

- ftrace
- ltrace

# perf

counting with `perf stat`:

```bash
perf list # list 可观察指标
perf stat -e ${LIST} ${CMD}
perf stat -p ${PID} sleep 1 # 观察进程 1 秒
```

sampling with `perf record`:

```bash
x
```



# valgrind



# Jepsen



https://unix.stackexchange.com/questions/128953/how-to-display-top-results-sorted-by-memory-usage-in-real-time

https://www.linuxprogrammingblog.com/io-profiling