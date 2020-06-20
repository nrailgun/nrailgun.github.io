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

