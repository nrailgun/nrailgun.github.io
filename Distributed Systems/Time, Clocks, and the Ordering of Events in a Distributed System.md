## Introduction

A system is distributed if the message transmission delay is not negligible compared to the time between events in a  single process. In a distributed system it's sometimes impossible to say that one of the 2 events occurred first.

## The Partial Ordering

We assume that the system is composed of a collection of processes. Each process consists of a sequence of events.

*Definition*. The "**happened before**" relation "$\to$" on the set of events of a system is the smallest relation satisfying the following 3 conditions:

1. If $a$ and $b$ are events in the same process, and $a$ comes before $b$, then $a \to b$.
2. If $a$ is the sending of a message by one process and $b$ is the receipt of the same message by another process, then $a \to b$.
3. if $a \to b$ and $b \to c$, then $a \to c$.

Two events $a$ and $b$ are said to be **concurrent** if $a \not \to b$ and $b \not \to a$.

## Logical Clocks

We define a clock $C_i$ for each process $P_i$ to be a function which assigns a number $C_i\left(a\right)$ to any event $a$ in that process. The entire system of clocks is represented by the function $C$ which assigns to any event $b$ the number $C\left(b\right)$. where $C\left(b\right)=C_j\left(b\right)$ if b is an event in process $P_j$.

***Clock Condition***. For any events $a$, $b$: if $a \to b$, then $C\left(a\right) \lt C\left(b\right)$.

Clock Condition is satisfied if the following 2 conditions hold.

- C1​. If $a$ and $b$ are events in process $P_i$, and $a$ comes before $b$, then $C_i\left(a\right) < C_i\left(b\right)$.
- C2. If $a$ is the sending of a message by process $P_i$, and $b$ is the receipt of that message by process $P_j$, then $C_i\left(a\right) < C_j\left(b\right)$.

To guarantee that the system of clocks satisfies the Clock Condition, we will insure that satisfies conditions C1 and C2. To meet C1 and C2, implementation rules IR1 and IR2 must be obeyed.

- IR1. Each process $P_i$ increments $C_i$ between any 2 successive events.

- IR2.

  - If event $a$ is the sending of a message $m$ by process $P_i$, then the message contains a timestamp   $T_m = C_i(a)$.

  - Upon receiveing a message $m$, process $P_j$ sets $C_j$ greater than or equal to its present value greater than $T_m$.

## Ordering the Events Totally

We define a relation $\Rightarrow$ as follows: if $a$ is an event is process $P_i$ and b is an event in process $P_j$, them $a \Rightarrow b$ iff either

1. $C_i(a) \lt C_j(b)$

2. $C_i(a) = C_j(b)$ and $P_i \lt P_j$.

It's easy to see that this defines a total ordering and that the Clock Condition implies that if $a \to b$ then $a \Rightarrow b$. Being able to totally order the events can be very userful in implementing a distributed system.

We wish to find an algorithm for granting the resource to a process which satisifies the following 3 conditions:

1. A process which has been granted the resource must release it before it can be granted to an other process.
2. Different requests for the resource must be granted in the order in which they are made.
3. If every process which is granted the resource eventually releases it, then every request is eventually granted.

To solve the problem, we implement a system of clocks with rules IR1 and IR2, and use them to define a total ordering $\Rightarrow$ of all events. To simplify the problem, we make a assumption that messages tranlations are ordered and repliable (which can be easily satisfied by TCP).

The algorithm is then defined by the following 5 rules.

1. To request the resource, process $P_i$ sends the message *request resource* $(P_i, T_m)$ to **every other** process, and puts that message on its request queue, where $T_m$ is the timestamp of the message.

