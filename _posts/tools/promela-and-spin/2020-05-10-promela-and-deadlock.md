---
layout: post
title: "Promela and deadlock"
categories: promela-and-spin
date: 2020-05-10 00:00:00
---

﻿# 死锁的必要条件

形成死锁，必须满足 4 个必要条件：

 - 互斥条件
 - 非剥夺条件
 - 请求与保持条件
 - 循环等待条件

用程序员的话来翻译，应该是：

 - 对象被互斥锁保护；
 - 锁只能被拥有锁的进程释放；
 - 进程持锁等待；
 - 进程互相等待。
 
满足以上 4 点，你就很可能要死锁了。

# 交叉 interleaving 与 原子操作 atomic
定义进程 $p_i = (s_{i0}, s_{i1}, \dots)$，其中 $s_{ij}$ 表示进程中的原子指令。给定进程 $p_i$ 和 $p_j$，他们的 interleaving 为 $(i_0, i_1, i_2, \dots)$。设 $i_k = s_{im}$, $i_l = s_{in}$，$m \lt n$， 则 $k \lt l$。简单地说就是，两个进程按保持原子操作顺序交叉。

原语级别的 atomic 显然并不足够。比如，在 C 中使用标志变量：
```C
if (usable) {
    usable = 0;
}
```
由于进程交叉，必将导致竞争条件，重复修改标志。所以，计算机要提供定义更加复杂原子操作的能力。在 `promela` 建模中，`promela` 提供了 `atomic` 关键字来定义原子操作。
```
atomic {
    if
    :: usable ->
        usable = false;
    fi
}
```

# 原子操作阻塞
进程可能在持锁过程中遭遇阻塞，这个时候通常必需释放锁。`pthread` 的接口更加直接：
```
int pthread_cond_wait(pthread_cond_t *cond, pthread_mutex_t *mutex);
```
你要等待条件成立，至少要释放条件相关的锁，代码得以执行，条件才能成立。`promela` 的 `atomic` 也是如此：
> DESCRIPTION
If a sequence of statements is enclosed in parentheses and prefixed with the keyword atomic , this indicates that the sequence is to be executed as one indivisible unit, non-interleaved with other processes. In the interleaving of process executions, no other process can execute statements from the moment that the first statement of an atomic sequence is executed until the last one has completed. The sequence can contain arbitrary Promela statements, and may be non-deterministic.

> If any statement within the atomic sequence blocks, atomicity is lost, and other processes are then allowed to start executing statements. When the blocked statement becomes executable again, the execution of the atomic sequence can be resumed at any time, but not necessarily immediately. Before the process can resume the atomic execution of the remainder of the sequence, the process must first compete with all other active processes in the system to regain control, that is, it must first be scheduled for execution. 

由于 `promela` 给出的 beginner tutorial 只说明 `atomic` 防止了 interleaving，却没有讨论阻塞，因而产生了巨大的误会与不解。

# 断言 assert
我喜欢 `assert`，虽然 `assert` 不能发现所有问题，但是能及早发现很多问题。在多线程程序中，理论上 `assert` 不一定能找出竞争条件导致的断言失败，实践中却可能是非常有用的。
```C
if (usable) {
    assert(usable);
    usable = 0;
}
```
