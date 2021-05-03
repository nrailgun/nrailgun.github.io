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

http://www.brendangregg.com/perf.html

# dstat

x

# gdb

gdb 可以查看 python 中 c++ 是如何挂掉的（UPDATE：or `gdb --args python main.py`）。 

```text
file python
run main.pys
bt
```

选中线程

```
info threads
thread tid
```

打印变量

```
select-frame 0
info locals
p varname
```

# valgrind

```bash
valgrind --tool=memcheck --leak-check=full ${CMD} ${ARGS} >out 2>&1
```

# Jepsen

https://unix.stackexchange.com/questions/128953/how-to-display-top-results-sorted-by-memory-usage-in-real-time

https://www.linuxprogrammingblog.com/io-profiling

# Linux BPF

http://www.brendangregg.com/Slides/LISA2019_Linux_Systems_Performance.pdf

# 查看指标

### Memory Usage

```bash
cat /proc/$pid/status | grep Vm
```

### Boot Time

```bash
ps -eo pid,lstart,cmd
```

### Threads

```bash
top -H -c -p `pgrep -d',' -f psstorproxy`
```

# 分析 log

个人还是喜欢 py，方便又强大。

```python
import re, sys
from functools import cmp_to_key
from statistics import mean

with open(sys.argv[1], 'r') as f:
  lines = f.readlines()

prog = re.compile(
	'^INFO:tensorflow:loss = (\w+.\w+), step = (\w+)'
    )

reqinfos = []
for line in lines:
  result = prog.match(line)
  if not result:
    continue

  print(result.group(1))
```

如果需要还可以用 matplotlib 画图

```python
import matplotlib.pyplot as plt

x = [1, 2, 3]
y = [4, 5, 6]
plt.plot(x, y, 'bo', label='weps + ppipe')
plt.show()
```





