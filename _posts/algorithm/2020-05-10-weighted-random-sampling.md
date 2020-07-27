---
layout: post
mathjax: true
title: "加权随机采样算法"
categories: algorithm
date: 2020-05-10 00:00:00
---

﻿加权随机采样 Weight Random Sampling (WRS) 可以用下列算法伪代码定义。

- Given
	- A population $V$ of $n$ weighted items
- Let $S = \emptyset$
- For $k \in [1, m]$ do
	- Let $p_i = \frac {w_i} {\sum_{s_j \in V - S} w_j}$ be the probability of item $v_i$ to be picked
	- Randomly pick an item $v_i \in V - S$ and insert it in $S$
- End-For
- Return $S$

## Algorithm R

Algorithm R 是**平均加权**随机采样（uniform random sampling）的经典解决方案（$w_i = w_j$ for any $i, j \in [1, n)$）。论文参见 [Vitter, Jeffrey S. "Random sampling with a reservoir." _ACM Transactions on Mathematical Software (TOMS)_ 11.1 (1985): 37-57.](http://www.cs.umd.edu/~samir/498/vitter.pdf)。

- Let $S = \emptyset$
- For $i \in [1, m]$ do
	- Insert $v_i$ into $S$
- End-For
- For $i \in [m+1, n]$ do
	- pick item $v_i$ with a probability of $p = \frac m i$
	- randomly pick an item from $S$ and replace it with $v_i$
- End-For
- Return $S$

时间复杂度 $O(n)$，空间复杂度 $O(m)$。

J. Vitter 还有加权随机采样的方法：J. Vitter, Faster methods for random sampling, Communications of the ACM, 27 (1984),  pp. 703–718，不过我没有仔细查看。

## Algorithm A-Res

A-Res 是加权平均采样的经典算法之一，论文参见 [Efraimidis, Pavlos S., and Paul G. Spirakis. "Weighted random sampling with a reservoir." _Information Processing Letters_ 97.5 (2006): 181-185.](https://www.sciencedirect.com/science/article/pii/S002001900500298X)。

- given
	- A population $V$ of $n$ weighted items
- let $R = \emptyset$
- insert 1st $m$ items into $V$
- for each $v_i$ in R
	- $k_i = u_i^{\frac 1 {w_i}}$, where $u_i = \mathrm{rand}(0, 1)$ (inclusive)
- for $i \in [m+1, n]$ do
	- pick smallest $k_i$ in $R$ as $T$
	- $k_i = u_i^{\frac 1 {w_i}}$, where $u_i = \mathrm{rand}(0, 1)$ (inclusive)
	- if $T \gt k_i$ then
		- replace item $i$ in $R$ with $v_i$

时间复杂度 $O(n \log m)$，空间复杂度 $O(m)$。

Algorithm A-Res 有两个优点，一是可以使用权重，二是 1 pass online 计算，无需整个权重数组，适用于大数据中的数据流处理（但是这个问题对于电子游戏应该是一般不存在的）。

## Wong's Method

论文参见 [Wong, Chak-Kuen, and Malcolm C. Easton. "An efficient method for weighted sampling without replacement." _SIAM Journal on Computing_ 9.1 (1980): 111-113.](https://epubs.siam.org/doi/pdf/10.1137/0209009)。

该论文发表于 1980 年，与 A-Res 处理相同的问题（加权随机采样），不过，而 A-Res 发表于 2005 年，适用于大数据的数据流处理（2004 年 Google 发表了 Map Reduce 的 Paper）。

算法的实现非常简单，首先，将权重构建为二叉树（初始化过程 $O(n)$），在查找过程中递归下降搜索$(O(\log m)$，并重新整理权重（$O(n)$）。

如果 $m$ 较小，$n$ 较大，比起重新构建 $O(n)$ 时间重建二叉树，记录修改过程并还原。

```lua
function wrs(t, n)
        local nodes = {}
        for k, w in pairs(t) do
                local node = {k = k, w = w, tw = w}
                table.insert(nodes, node)
        end
        for i = #nodes, 2, -1 do
                local parent_idx = math.floor(i / 2)
                nodes[parent_idx].tw = nodes[parent_idx].tw + nodes[i].tw
        end

        local ret = {}
        for i = 1, n do
                local gas = nodes[1].tw * math.random()
                local j = 1
                while gas >= nodes[j].w do
                        gas = gas - nodes[j].w
                        j = j * 2
                        if gas >= nodes[j].tw then
                                gas = gas - nodes[j].tw
                                j = j + 1
                        end
                end
                table.insert(ret, nodes[j].k)

                -- adjust weight
                local w = nodes[j].w
                nodes[j].w = 0
                while j > 0 do
                        nodes[j].tw = nodes[j].tw - w
                        j = math.floor(j / 2)
                end
        end
        return ret
end
```

