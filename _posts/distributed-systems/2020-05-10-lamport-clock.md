---
layout: post
mathjax: true
title: "Lamport Clock"
categories: distributed-systems
date: 2020-05-10 00:00:00
---

## Introduction

***A system is distributed if the message transmission delay is not negligible compared to the time between events in a  single process***. In a distributed system it's sometimes impossible to say that one of the 2 events occurred first.

## The Partial Ordering

We assume that the system is composed of a collection of processes. Each process consists of a sequence of events.

*Definition*. The "**happened before**" relation "$\to$" on the set of events of a system is the smallest relation satisfying the following 3 conditions:

1. If $a$ and $b$ are events in the same process, and $a$ comes before $b$, then $a \to b$.
2. If $a$ is the sending of a message by one process and $b$ is the receipt of the same message by another process, then $a \to b$.
3. if $a \to b$ and $b \to c$, then $a \to c$.

Two events $a$ and $b$ are said to be **concurrent** if $a \not \to b$ and $b \not \to a$.

## Logical Clocks

We define a clock $C_i$ for each process $P_i$ to be a function which assigns a number $C_i\left(a\right)$ to any event $a$ in that process. The entire system of clocks is represented by the function $C$ which assigns to any event $b$ the number $C\left(b\right)$. where $C\left(b\right)=C_j\left(b\right)$ if b is an event in process $P_j$.

**Clock Condition**. For any events $a$, $b$: if $a \to b$, then $C\left(a\right) \lt C\left(b\right)$.

Clock Condition is satisfied if the following 2 conditions hold.

- **C1**​. If $a$ and $b$ are events in process $P_i$, and $a$ comes before $b$, then $C_i\left(a\right) < C_i\left(b\right)$.
- **C2**. If $a$ is the sending of a message by process $P_i$, and $b$ is the receipt of that message by process $P_j$, then $C_i\left(a\right) < C_j\left(b\right)$.

To guarantee that the system of clocks satisfies the Clock Condition, we will insure that satisfies conditions C1 and C2. **To meet C1 and C2, implementation rules IR1 and IR2 must be obeyed**.

- **IR1**. Each process $P_i$ increments $C_i$ between any 2 successive events.

- **IR2**.
  - If event $a$ is the sending of a message $m$ by process $P_i$, then the message contains a timestamp   $T_m = C_i(a)$.

  - Upon receiveing a message $m$, process $P_j$ sets $C_j$ greater than or equal to its present value greater than $T_m$.

## Ordering the Events Totally

We define a relation $\Rightarrow$ as follows: if $a$ is an event is process $P_i$ and b is an event in process $P_j$, them $a \Rightarrow b$ iff either

1. $C_i(a) \lt C_j(b)$

2. $C_i(a) = C_j(b)$ and $P_i \lt P_j$.

It's easy to see that this defines a total ordering and that the Clock Condition implies that if $a \to b$ then $a \Rightarrow b$. Being able to totally order the events can be very userful in implementing a distributed system.

We wish to find an algorithm for granting the resource to a process which satisifies the following 3 conditions:

1. **GC1**. A process which has been granted the resource must release it before it can be granted to an other process.
2. **GC2**. Different requests for the resource must be granted in the order in which they are made.
3. **GC3**. If every process which is granted the resource eventually releases it, then every request is eventually granted.

To solve the problem, we implement a system of clocks with rules IR1 and IR2, and use them to define a total ordering $\Rightarrow$ of all events. To simplify the problem, we make a assumption that messages tranlations are ordered and repliable (which can be easily satisfied by TCP).

**The algorithm is then defined by the following 5 rules**.

1. To request the resource, process $P_i$ sends the message *request resource* $(P_i, T_m)$ to **every other** process, and puts that message on its request queue, where $T_m$ is the timestamp of the message.
2. When  process $P_j$ receives the message *request resource* $(P_i, T_m)$, it places it on ties request queue and sends a timestamped acknowledge message to $P_i$.
3. To release the resource, process $P_i$ removes any *request resource* $(P_i, T_m)$ message from its request queue and sends a (timestamped) *release resource* to every other process.
4. When process $P_j$ receives a *releases resource* message, it removes any *request resource* $(P_i, T_m)$ message from its request queue.
5. Process $P_i$ is granted the resource when the following 2 conditions are satisified:
   1. There is a *request resource* $(P_i, T_m)$ in its request queue which is ordered before any other request in its queue which is ordered before any other request in its queue by the relation $\Rightarrow$.
   2. **$P_i$ has received a message from every other process timestamped later than $T_m$**.

It's easy to verify that the algorithm satifies condition GR1, GR2 and GR3.

This algorithm is distributed. However this algorithm requires the active participation of all the processes, and must know all the commands issued by other processes, so the failure of a single process will make the system unavailable. The problem of failure is a diffcult one. ***Without physical time, there is no way to distinguish a failed process from one which is just pausing between events***.

## Anomalous Behavior

"**Anomalous Behavior**". Person $A$ issues a request $A$ on a computer $A$, and telephone person $B$ to issue request $B$ on a different computer $B$. It's possible for request $B$ to receive a lower timestamp and be ordered before request $A$ (since **the precedence information is based on mesages *external* to the system**).

**Strong Clock Condition**. For any events $a$, $b$ in $\mathscr{G}$, if $a \to' b$, then $C(a) \lt C(b)$.

This is stronger than the ordinary Clock Condition because $\to'$ is stronger relation than $\rightarrow$. It's not general satisfied by the logical clock.

## Physical Clocks

Let $C_i(t)$ denotes the reading of the clock $C_i$ at physical time $t$. In order for the clock $C_i$ to be a true physical clock, we will assume that the following conditions are satisified:

- **PC1**. There exists a constant $\mathcal K \ll 1$ such that, for all $i$, $|\frac{d C_i(t)}{dt} - 1| \lt \mathcal K$.
- **PC2**. There exists a sufficiently small constant $\epsilon$ such that, For all $i$, $j$: $|C_i(t) - C_j(t)| \lt \epsilon$.

We now specialize IR1 and IR2 for our physical clocks as follows:

- **IR1'**. For each $i$, if $P_i$ does not receive a message at physical time $t$, then $C_i$ is differentiable at time $t$ and $\frac{dC_i(t)}{dt} > 0$.
- **IR2'**.
  - If $P_i$ sends a message $m$ at physical time $t$, then $m$ contains a timstamp $T_m = C_i(t)$.
  - Upon receiving a message $m$ at time $t'$, process $P_j$ sets $C_j(t')$ to $\max \left( C_j \left( t' \right), T_m + \mu_m \right)$.

where $\mu_m$ is the assumed minimum delay.

We now show that this **clock synchronizing algorithm** can be used to satisfy PC2 (**PC2 is not always satisfied as it was in logical clock case**). We assume that the system is described by a directed graph in which an arc from process $P_i$ to process $P_j$ represents a comminication line over which messages are sent. The **diameter** of the directed graph is the smallest number $d$ such that there is a path between any $P_i$ and $P_j$ having at most $d$ arcs.

**THEOREM**. Assume a strongly connected graph of processes with **diameter** $d$ which always obeys rules $IR1'$ and $IR2'$. Assume that for any message $m$, $\mu_m \le \mu$ for some constant $\mu$, and that for all $t \ge t_0$:

1. PC1 holds.

2. There are constant $\tau$ and $\xi$ such that every $\tau$ seconds a message which an unpredictable delay less than $\xi$ is sent over every arc. Then PC2 is satisfied with
   $$
   \epsilon \approx d(2 \mathcal K \tau + \xi)
   $$
    for all $t \gt t_0 + \tau d$, where the approximations assume $\mu + \xi \ll \tau$.

---

lamport clock 有一个改良 vector clock，可参考：https://zhuanlan.zhihu.com/p/56886156 。

