## 思路

一般思路：

1. 先找一个 naive solution；
2. 在 naive solution 的基础上可以套用其他算法，加速查找的速度（比如线段树或者 KMP 加速搜索）；
3. 最后看看有没有特殊性质可以利用。

其他突破口：

1. 能否排序？

## 两串匹配

检测两个字符串 `s` 和 `p` 是否匹配，要用 DP 求解，`DP[i][j]` 表征常见思路：

1. 表示 `s[:i]` 和 `p[:j]` 是否匹配；

2. 表示 `s[i:]` 和 `p[j:]` 是否匹配。

不一定两者都能走通，一个走不通就换另一个角度想想。

题目：44. Wildcard Matching，10. Regular Expression Matching。

## 常数空间使用

如果没有特殊算法，一般是抠空间。比如：

1. 从符号位抠。
2. 从矩阵中抠一行出来用（73. Set Matrix Zeroes，[138. Copy List with Random Pointer](https://leetcode-cn.com/problems/copy-list-with-random-pointer/)）

这种是纯粹做题技巧，一般就是相当于偷一个符号位当做数组出来用，或者是偷一个指针来做映射。实际工程应该没什么参考意义，毕竟随便碰输入数据，出了问题要被 leader 锤到原地去世。

## 数列 / 字符串窗口问题

典型思路是双指针法维护一个滑动的窗口。题目：76. Minimum Window Substring。



## 等差数列

$$
a_n =a_1 + (n - 1) \times d \\
S_n = \frac n 2 (a_1 + a_n) = na_1 + \frac{n(n-1)}{2} d
$$

```c++
int arith_prog(int a0, int d, int i) {
	return a0 + i * d;
}
int arith_prog_sum(int a0, int d, int i) {
    return (i + 1) * a0 + (i + 1) * i * d / 2;
}
```

$i$ 是如何替换 $n$ 的呢？因为 $i + 1 = n$，替换即可。

## 等比数列

$$
a_n = a_1 q^{n-1} = a_iq^{n-i} \\
S_n = \frac{a_1(1-q^n)}{1-q} = \frac{a_1-a_nq}{1-q}
$$

```c++
int geo_series(int a0, int q, int i) {
    return a0 * pow(q, i);
}
int geo_series_sum(int a0, int q, int i) {
    return a0 * (1 - pow(q, i + 1)) / (1 - q);
}
```

## 公约数、公倍数

```c++
int gcd(int a, int b) {
	if (b == 0)
		return a;
	return gcd(b, a % b);
}
```

## Wildcard

只有 `'.'` 和 `'*'` 两种 wildcard，所以动规 `isMatch(s, i, p, j)` 递归检查即可（根据第一个 char 是否 match 来递归）。

## KMP

kmp 算法要先算 lps (**L**ongest **P**refix which is also **S**uffix)，有了 lps，过程很直观。

```c++
int kmp(const string &txt, const string &pat) {
    int n = txt.size(), m = pat.size();
    vector<int> lps = compute_lps(pat);
    int i = 0, j = 0;
    while (i < n) {
        if (txt[i] == pat[j]) { // 如果匹配，i/j 一直向前走；
            i++;
            if (++j == m)
                return i - m;
        }
        else { // 如果不匹配，利用和 prefix 匹配得上的 suffix。
            if (j == 0)
                i++;
            else
                j = lps[j - 1];
        }
    }
    return -1;
}

vector<int> compute_lps(const string &pat) { // Longest Prefix which is also Suffix
    int m = pat.size();
    vector<int> lps(m, 0);
    int i = 1, len = 0;
    while (i < m) {
        if (pat[i] == pat[len]) // suffix 和 prefix 能 match
            lps[i++] = ++len;
        else {
            if (len == 0) // 完全不 match，这里也很容易理解。
                lps[i++] = 0;
            // 要注意，len 是指 prefix 能 match 的长度，可以重复利用下在 len-1 处能 match 的 prefix。
            // 即使粗略能理解，说实话还是比较抽象。话又说回来，要是随便都能想到，Knuth 还要发论文解释这个算法？想啥呢...
            else
                len = lps[len - 1];
        }
    }
    return lps;
}
```

## 矩阵转置、旋转后的索引

转置
$$
M(i, j) = M^T(j, i) \\
M^T(i, j) = M(j, i)
$$
顺时针旋转
$$
M(i, j) = M'\left( j, \mathrm{col}(M) - 1 - i \right) \\
M'(i, j) = M\left( \mathrm{col}(M) - 1 - j, i \right)
$$
逆时针旋转
$$
M(i, j) = M'\left( \mathrm{row}(M) - 1 - j, i \right) \\
M'(i, j) = M\left(j, \mathrm{row}(M) - 1 - i \right)
$$
顺时针旋转例子

```c++
void rotate_ij(int n, int i, int j, int &ni, int &nj) {
    ni = j;
    nj = n - 1 - i;
}
void rotate(vector<vector<int>> &mat) {
    int n = mat.size();
    for (int i = 0; i < (n + 1) / 2; i++) {
        for (int j = 0; j < n / 2; j++) {
            int v = mat[i][j], _i = i, _j = j;
            for (int k = 0; k < 4; k++) {
                int ni, nj;
                rotate_ij(n, _i, _j, ni, nj);
                swap(mat[ni][nj], v);
                _i = ni;
                _j = nj;
            }
        }
    }
}
```

## 排列组合

$$
P(n, k) = \frac{n!}{k!} = n(n-1)(n-2)...(n-k+1) \\
C(n, k) = \frac{P(n, k)}{k!}
$$

注意利用

- $C(n, 0) = C(n, n) = 1$

- $C(n, k) = C(n, n - k)$
- $C(n, k+1) = C(n, k) \times \frac{n-k}{k+1}$（可以算 $(a+b)^n = \sum_{k=0}^{n}C(n,k)a^{n-k}b^k$）

