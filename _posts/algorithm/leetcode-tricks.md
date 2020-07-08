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
2. 从矩阵中抠一行出来用（73. Set Matrix Zeroes）。

## 数列 / 字符串窗口问题

典型思路是双指针法维护一个滑动的窗口。

```c++
// Substring 类问题的模板：
int find_substr(string s) {
	int sbeg = 0, send = 0;
	int l = INT_MAX, head = 0;

	while (send < s.size()) {
		send++;
		// Make constraint invalid

		while (true /* Constraint satisfied */) {
			// Increase sbeg to make constraint invalid
			sbeg++;
		}
	}
	return l;
}
```

题目：76. Minimum Window Substring。

## 偷用输入数据

题目：[138. Copy List with Random Pointer](https://leetcode-cn.com/problems/copy-list-with-random-pointer/)

这种是纯粹做题技巧，一般就是相当于偷一个符号位当做数组出来用，或者是偷一个指针来做映射。实际工程应该没什么参考意义，毕竟随便碰输入数据，出了问题要被 leader 锤到原地去世。

## 等差、等比数列

我要吐了，说实话这种高中数学题经常性反应不过来。

