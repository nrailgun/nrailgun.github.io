---
layout: post
title: "Bloom Filter"
categories: algorithm
date: 2020-06-23 00:00:00
---

Bloom filter 联立 $M$ 个哈希函数 $H_i$，
$$
B_i = B_i \or H_i(x)
$$
如果查找过程中发现 $B_i$ 全部 match，大概率在集合中。存在 false positive 的问题，而且不支持删除。