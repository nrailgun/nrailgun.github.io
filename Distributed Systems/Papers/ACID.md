ACID = ([atomicity](https://en.wikipedia.org/wiki/Atomicity_(database_systems)), [consistency](https://en.wikipedia.org/wiki/Consistency_(database_systems)), [isolation](https://en.wikipedia.org/wiki/Isolation_(database_systems)), [durability](https://en.wikipedia.org/wiki/Durability_(database_systems)))。由于历史原因，有些概念的命名可能有时候令人迷惑。

## Atomicity

atomic transaction 是一系列不可再细分的操作，要么全部发生，要么完全不发生。

## Consistency

不同于分布式系统 CAP 定理中的 consistency，database 中的 consistency 是指 transaction 必须以合法的方式修改数据（requirement that any given database transaction must change affected data only in allowed ways），亦即数据完整性。

## Isolation

isolation 和 atomicity 强调不同的方面，atomicity 要求操作一起执行或者不执行，isolation 要求对于其他 process，transaction 仿佛是一个整体 integrity（比如同时观察到 2 个操作结果，或者 0 个操作结果）。

read phenomenas:

- dirty reads：读到了 unroll 的值。
- lost updates：进行到一半，写的值被其他 transaction 覆盖。
- non-repeatable reads：进行到一半，后部分读到了其他 transaction commit 的值。
- phantom reads：进行到一半，后部分读到了其他 transaction commit 的 row。

| isolation level \ read phenomenas | dirty reads  | lost updates | non-repeatable reads |   phantoms   |
| :-------------------------------: | :----------: | :----------: | :------------------: | :----------: |
|         read uncommitted          | $\checkmark$ | $\checkmark$ |     $\checkmark$     | $\checkmark$ |
|          read committed           |              | $\checkmark$ |     $\checkmark$     | $\checkmark$ |
|          repeatable read          |              |              |                      | $\checkmark$ |
|           serializable            |              |              |                      |              |

从结果上看，如果执行结果等同于 transaction 一个个无重叠地执行的结果，那么 transaction schedule 是 serializable 的（a transaction schedule is serializable if its outcome (e.g., the resulting database state) is equal to the outcome of its transactions executed serially）。

2 PL (2 Phase Locking) 是实现 serializability 的常用方法，分为两个阶段：Expanding（只能加锁）和 Shrinking（只能解锁）。可以很直觉地理解为何如此可以避免 read 到事务未完成的中间状态。

## Linearizability vs Serializability

两者强调不同的方面。Linearizability（可线性化 / 线性一致性）也称为 Atomic Consistency（原子一致性），是一种一致性。

Serializability（可串行化）是一种隔离性。

## REFs

- [ACID](https://en.wikipedia.org/wiki/ACID)
- [Isolation](https://en.wikipedia.org/wiki/Isolation_(database_systems))
- [Strong Consistency Models](https://aphyr.com/posts/313-strong-consistency-models)

