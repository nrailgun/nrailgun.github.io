---
layout: post
title: "Product Quantition based Fast Matrix Multiplication"
categories: algorithm
date: 2020-05-10 00:00:00
---

﻿
Conventional Matrix-Vector Multiplication:
$$
y(i) = \sum_{j=1}^n W(i, j) \times x(j)
$$

---

*Product Quantization based Matrix-Vector Multiplication* (*PQ* for short):

$$
P(c, i, j) = W \left( i, jd : (j+1) d \right) \centerdot C_c
$$

$$
y(i) \approx \sum_{j=1}^{\frac n d} P(c, i, j)
$$

`$P$` for the pre-computation table, `$c$` for quantization centroid index, `$C$` for quantization center set, `$d$` and `$b$` for quantization paramaters.

---

$$
y \approx \sum_{j=1}^{\frac n d} P(c, :, j)
$$
