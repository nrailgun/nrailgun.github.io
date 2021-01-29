---
layout: post
title: "Replacement"
categories: uncategorized
date: 2021-01-24 00:00:00
---

# LRU

lru 是最常见的 replacement。

# Clock

> Clock is a more efficient version of FIFO than Second-chance because  pages don't have to be constantly pushed to the back of the list, but it performs the same general function as Second-Chance. The clock  algorithm keeps a circular list of pages in memory, with the "hand"  (iterator) pointing to the last examined page frame in the list. When a  page fault occurs and no empty frames exist, then the R (referenced) bit is inspected at the hand's location. If R is 0, the new page is put in  place of the page the "hand" points to, and the hand is advanced one  position. Otherwise, the R bit is cleared, then the clock hand is  incremented and the process is repeated until a page is replaced.

## WS Clock

1. 当待缓存对象存在缓存中时，更新 rt 为当前时间。同时，指针指向该对象的下一个对象。
2. 若不存在于缓存中时，如果缓存没满，则更新指针指向位置的 rt 为当前时间，R 为 1。同时，指针指向下一个对象。如果满了，则需要淘汰一个对象。检查指针指向的对象：
   1. R 为 1，说明对象在 working set 中，则重置 R 为 0，指针指向下一个对象。
   2. R 为 0。如果 age 大于 t，说明对象不在 working set 中，则替换该对象，并置 R 为 1，rt 为当前时间。如果 age 不大于 t，则继续寻找淘汰对象。如果回到指针开始的位置，还未寻找到淘汰对象，则淘汰遇到的第一个 R 为 0 的对象。age 表示为当前时间和 rt 的差值。

