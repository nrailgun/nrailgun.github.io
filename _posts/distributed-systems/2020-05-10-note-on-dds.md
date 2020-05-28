---
layout: post
title: "《Designing Distributed Systems》笔记"
categories: distributed-systems
date: 2020-05-10 00:00:00
---

# Note about *Designing Distributed Systems*

本文为 *Designing Distributed Systems: PATTERNS AND PARADIGMS FOR SCALABLE, RELIABLE SERVICES* 的笔记。个人认为，本书具有一定的指导意义，总结了一些经验性的分布式系统设计模式，但并不涉及理论知识和实现细节。书中 *hands on* 部分大量使用 K8S / Docker / CoreOS 产品。本书英文版不过 130+ pages，阅读速度极快，作为入门，性时比尚可。

## Single Node Patterns

Single node 主要是指单个节点内的多服务协同。

### Sidecar

在同一 pod 内使用一个服务为另一个服务提供额外功能。例如，https 转发，限流器。

### Ambassador

代理服务对外访问。例如服务原来只访问一个数据节点，后来数据节点被 shard，用一个服务来代理访问 shard 的复杂操作。

### Adapter

转换各种不同标准的 API 接口，比如各种 HTTP / JSON / XML 转来转去。

公司大了，标准就多。标准多不算可怕，SB 多更可怕。

## Serving Patterns

Serving patterns 介绍了一些多节点的设计模式。

### Replicated Load-Balance

无状态冗余。

### Sharded Services

Stateful sharding。算法太复杂，书里草草介绍。

### Scatter / Gather

就粗暴理解为 map / reduce 吧。

### Functions and Event-Driven Processing

没看懂，看起来就是微服务。

### Ownership Election

就是一致性存储，感觉写得一般。

## Batch Computation Patterns

和 serving patterns 不同，batch computation 是离线操作，对稳定性，时效性要求较低。

### Work Queue Systems

无状态工人一个个来取 task。

### Event-Driven

类似 linux pipeline。

### Coordinated

很像 map reduce。