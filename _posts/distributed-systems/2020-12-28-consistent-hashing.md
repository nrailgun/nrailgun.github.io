---
layout: post
mathjax: true
title: "Consistent Hashing and Jump Hashing"
categories: distributed-systems
date: 2020-12-28 00:00:00
---

# Consistent Hashing and Random Trees

## Random Tree

假定对于所有的机器，所有的 cache 机器已知。

1. 当浏览器请求页面，从 $C$ 个节点的 $d$-nary abstract tree 中随机选取一个 leave to root path。$C$ 是 cache 机器集合 $\mathcal C$ 的 size。使用哈希函数 $h$ 将 path 中的节点映射到一个 cache 机器，尝试请求页面。

2. 当 cache 机器收到请求，如果 page 存在于 cache 中，那么直接返回；否则增加页面的计数，并按照 browser 指定的 path，向上一层的节点请求液面。如果页面的计数到达了一个阈值 $q$，cache 机器会向 page 服务器要求伺服一份 cache。

为什么这个方法可以避免热点呢？因为：

1. 显然，page 不能都集中在一个 server 上，否则肯定很容易 swamped。通过将 page 分配到逐个 server 中能比较好地解决这个问题。
2. 但是即使一个机器只有一个页面，如果这个页面非常受到欢迎，那么单个 cache 仍然很容易被 swamped。所以我们需要一个树形的结构。如果页面不受欢迎，只会在靠近根部节点才有足够多的 req，才会进行缓存（更少的缓存服务器节约成本）。如果页面收到欢迎，那么叶子处也会有非常多请求，那么就会有非常多的叶子处的缓存（更多 cache 服务器来分摊压力）。
3. 直观上理解，靠近根部的 cache 机器伺服更多的页面，即使页面并不是热点，也容易被 swamped。因此，对每一个页面，abstract tree 都是随机生成的不同的树，这确保底部节点不会伺服太多页面，因此不太会被 swamp。树的 root 是特殊的，不是 cache 而是 page server。

如此，random tree 方法在 $\Theta (\log C)$ 的 delay 的代价下避免了 cache 被 swamp。

## Consistent Hashing

论文的写法比较抽象：给定随机函数 $r_B$ 和 $r_I$，$f_V(i)$ 被定义为 $b \in V$ 使得 $|r_B(b) - r_I(i)|$ 最小化。

其实际上的意思是，将桶 $b$ 通过哈希 $r_B$ 分布到一个区间（例如 $[0, 2^{31-1}]$），$i$ 通过哈希 $r_I$ 进行映射，并分配到其附近的桶中。

<img src="https://images2015.cnblogs.com/blog/498077/201608/498077-20160822172901526-169091807.png" alt="一致性哈希图解" style="zoom:50%;" />

如果增加、减少 bucket，那么只影响附近两个 bucket。此外，为了减少数据倾斜，一般每个节点都会插入一定量的虚拟节点。

---

Hash function properties:

1. smoothness: when a machine is added to or removed from the set of caches, the expected fraction of objects that must be moved to a new cache is the minimum needed to maintain a balanced load across the caches.
2. spread: over all the client views, the total number of different caches to which a object is assigned is small.
3. load:  over all the client views, the number of distinct objects assigned to a particular cache is small.

spread 的好处是 object 所在机器比较少，节约存储。load 的好处是某个 cache 不会存太多 obj。smoothness 的好处是变更时候变动比较少，更平滑。

最重要的是 monotonicity，从 $V_1$ 到 $V_2$ object $i$ 只会从旧 cache 移动到新 cache，不会在旧 cache 内部移动。

# A Fast, Minimal Memory, Consistent Hash Algorithm

```c++
int32_t JumpConsistentHash(uint64_t key, int32_t bucket_size) {
  int64_t b = -1, j = 0;
  while (j < bucket_size) {
    b = j;
    key = key * 2862933555777941757ULL + 1;
    j = (b + 1) * (double(1LL << 31) / double((key >> 33) + 1));
  }
  return b;
}
```

