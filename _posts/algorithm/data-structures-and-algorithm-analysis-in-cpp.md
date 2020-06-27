# 数据结构与算法分析：C++ 描述

## 引论

#### 对数

$$
\log_AB = \frac{\log_CB}{\log_CA}; A,B,C \gt 1, A \ne 1
$$

$$
\log AB = \log A + \log B
$$

#### 级数

$$
\sum_{i=0}^N 2^i = 2^{N+1}-1
$$

$$
\sum_{i=0}^N A^i = \frac{A^{N+1}-1}{A-1}
$$

如果 $0 \lt A \lt 1$，那么
$$
\sum_{i=0}^N A^i \le \frac{1}{1-A}
$$

$$
\sum_{i=1}^N i^2 = \frac{N(N+1)(2N+1)}{6} \approx \frac{N^3}{3}
$$

$$
\sum_{i=1}^N i^k \approx \frac{N^{k+1}}{|k+1|}
$$

## 算法分析

如果 $T_1(N) = O(f(N)), T_2(N) = O(g(N))$，那么

1. $T_1(N) + T_2(N) = O(f(N) + g(N))$
2. $T_1(N)T_2(N) = O(f(N) g(N))$

对任意常数 $k$，$\log^k(N) = O(N)$，对数增长缓慢。

如果 $f(N)$ 和 $g(N)$ 的极限为正无穷，可用洛必达法则计算相对增长率。
$$
\lim_{N\to\infty}\frac{f(N)}{g(N)} = \lim_{N\to\infty}\frac{f'(N)}{g'(N)}
$$
通常，如果算法在常数时间将问题大小削减为一部分（通常是一般），那么时间复杂度是 $O(\log N)$。

## 并查集

```c++

class DisjSets {
public:
        vector<int> s_;
        DisjSets(size_t n) : s_(n, -1) {
        }
        // 根据高度合并，尽量压低高度。`-s_[i]` 表示实际高度。
        void union_set(int r1, int r2) {
                if (r1 == r2)
                        return;
                if (s_[r1] > s_[r2])
                        s_[r1] = r2;
                else {
                        if (s_[r1] == s_[r2])
                                s_[r1]--;
                        s_[r2] = r1;
                }
        }
        int find(int x) {
                if (s_[x] < 0)
                        return x;
                return find(s_[x]);
                // return s_[x] = find(s_[x]); // 这种是 find 路径压缩
        }
        int count_set() const {
                int n = 0;
                for (int i = 0; i < s_.size(); i++) {
                        if (s_[i] < 0)
                                n++;
                }
                return n;
        }
};
```

## 图算法

### 拓扑排序

不停输出 in-degree 的 0 的 vertex，并将其连接 vertex in-degree 减 1。

### 无权最短路径

最短路径特例，相当于 $w_i=1$，BFS。

### 有权最短路径

```c++
class Solution {
public:
        using Tii = tuple<int, int>;
        int networkDelayTime(vector<vector<int>> &edges, int n, int k) {
                vector<vector<Tii>> adjs(n);
                for (auto &e : edges) {
                        int i = e[0] - 1;
                        int j = e[1] - 1;
                        int w = e[2];
                        adjs[i].emplace_back(j, w);
                }
                vector<int> dists(n, INT_MAX);
                dists[--k] = 0;

                priority_queue<Tii, vector<Tii>, greater<Tii>> q;
                q.push(make_tuple(0, k));
                vector<bool> visited(n, false);
                while (!q.empty()) {
                        int d, i; {
                                Tii t = q.top();
                                q.pop();
                                d = get<0>(t);
                                i = get<1>(t);
                        }
                        visited[i] = true;

                        for (const auto adj : adjs[i]) {
                                int j = get<0>(adj);
                                int w = get<1>(adj);
                                if (visited[j])
                                        continue; // 这是一步非必须的优化，但是可以减低 adjs 的 `push_heap` 时间。
                                if (dists[i] + w < dists[j]) {
                                        dists[j] = dists[i] + w;
                                        q.emplace(dists[j], j);
                                }
                        }
                }
                int maxd = *max_element(dists.begin(), dists.end());
                return maxd == INT_MAX ? -1 : maxd;
        }
};
```

### 负值边图

其实和 dijstra 算法是接近的，但是不允许存在负值环路，否则算法就可以无限循环了。

### 最大流

贪心选取最大流路径，在建立路径后也要多设置一条“反悔”回路。只支持有理数，但是计算机只有有理数。

### 最小生成树

Prim 算法：从源点出发，不停

- 寻找下一个 $w$ 最小的 $(u, v, w)$；其中，$u$ 是 known vertex，$v$ 是 unknown vertex。
- 标记 $v$ 为 known。

Kruskal 算法：

有 $n$ 个节点，寻找 $n-1$ 条边：

- 优先队列找出最短边 $(u, v, w)$，
- 看 $u$ 和 $v$ 是否已经连接（并查集），如果未连接，连接并选中该边。

