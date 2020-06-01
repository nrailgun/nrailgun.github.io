---
layout: post
title: "Modeling Distributed Systems with Spin Chan"
categories: promela-and-spin
date: 2015-05-10 00:00:00
---

Distributed systems consist of:

 - nodes
 - communication channels connecting nodes
 - protocols controlling data flow among nodes

Spin simulates distributed systems with processes and `chan`s.

## Declaration
A variable of channel type is declared by initializer.
```c
chan c = [ capacity ] of { type_1, type_2, ..., type_n };
```
If `capacity` $\ge 1$, channel is called "buffered", else "rendezvous" (直连，无缓冲).

## Send and Receive
Send statement has the form:
```c
c ! expr_1, expr_2, ..., expr_n;
```
Receive statement has the form:
```c
c ? var_1, var_2, ..., var_n;
```
Attension: ***Rendezvous `chan !` and `chan ?` pairs can't be interleaved. But interleavings occur in buffered `chan`***.

## Send chan through chan
`chan` can also be sent through `chan`, setting up a private connection between server and client.
```c
chan a = [0] of { int };
chan b = [0] of { chan };

b ! a;
```

## Test chan full / empty
Also, you can check channels for full / empty with `full`, `nfull`, `empty`, and `nempty`. ***Don't use the negative operator !***

## Peek chan
Syntax for receiving messages without removing it:
```c
ch ? <v1, v2, ..., vn>
```

## Pattern matching
Receive statement admits values as arguments. Receive statement is executable if and only if matching succeeds.
```c
c ? 'D', 'E', 'A', v;
```

## Keep in mind

 - Buffered channels are part of states
 - Don't use unless necessary
 - Set capacity as low as possible