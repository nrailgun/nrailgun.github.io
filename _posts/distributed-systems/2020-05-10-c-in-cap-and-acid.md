---
layout: post
title: "C in CAP and ACID"
categories: distributed-systems
date: 2020-05-10 00:00:00
---

## ACID

ACID = ([atomicity](https://en.wikipedia.org/wiki/Atomicity_(database_systems)), [consistency](https://en.wikipedia.org/wiki/Consistency_(database_systems)), [isolation](https://en.wikipedia.org/wiki/Isolation_(database_systems)), [durability](https://en.wikipedia.org/wiki/Durability_(database_systems)))。由于历史原因，有些概念的命名可能有时候令人迷惑。

### Atomicity

atomic transaction 是一系列不可再细分的操作，要么全部发生，要么完全不发生。

### Consistency

不同于分布式系统 CAP 定理中的 consistency，database 中的 consistency 是指 transaction 必须以合法的方式修改数据（requirement that any given database transaction must change affected data only in allowed ways），亦即数据完整性（integrity）。

### Isolation

isolation 和 atomicity 强调不同的方面，atomicity 要求操作一起执行或者不执行，isolation 要求对于其他 process，transaction 仿佛是一个整体 integrity（比如同时观察到 2 个操作结果，或者 0 个操作结果）。

read phenomenas:

- dirty reads：读到了 unroll 的值。
- lost updates：进行到一半，写的值被其他 transaction 覆盖。
- non-repeatable reads：进行到一半，后部分读到了其他 transaction commit 的值。
- phantom reads：进行到一半，后部分（另一个变量）读到了其他 transaction commit 的 row（读到了两个不同 revision 的两个变量）。

| isolation level \ read phenomenas | dirty reads  | lost updates | non-repeatable reads |   phantoms   |
| :-------------------------------: | :----------: | :----------: | :------------------: | :----------: |
|         read uncommitted          | $\checkmark$ | $\checkmark$ |     $\checkmark$     | $\checkmark$ |
|          read committed           |              | $\checkmark$ |     $\checkmark$     | $\checkmark$ |
|          repeatable read          |              |              |                      | $\checkmark$ |
|           serializable            |              |              |                      |              |

从结果上看，如果执行结果等同于 transaction 一个个无重叠地执行的结果，那么 transaction schedule 是 serializable 的（a transaction schedule is serializable if its outcome (e.g., the resulting database state) is equal to the outcome of its transactions executed serially）。

2 PL (2 Phase Locking) 是实现 serializability 的常用方法，分为两个阶段：Expanding（只能加锁）和 Shrinking（只能解锁）。可以很直觉地理解为何如此可以避免 read 到事务未完成的中间状态。

## Consistency Model

strict consistency 是一个仅在理论上存在的 model，要求所有的操作都按照 wall-clock 定义的 invokation 顺序瞬间完成。

sequential consistency 仅要求观察顺序和写入顺序相同。

linearizability（atomic consistency）可以理解为强化版的 sequential consistency，要求立刻被之后的操作观察到。通常实践中，linearizability 已经是非常强的一致性保证了。

serializability（serializable consistency）要求结果等价于原子操作顺序执行，但对于执行顺序没有要求（比如可以随意调度同一个进程的操作的先后顺序，有时候会导致问题）。

## REFs

- [ACID](https://en.wikipedia.org/wiki/ACID)
- [Isolation](https://en.wikipedia.org/wiki/Isolation_(database_systems))
- [Strong Consistency Models](https://aphyr.com/posts/313-strong-consistency-models)
