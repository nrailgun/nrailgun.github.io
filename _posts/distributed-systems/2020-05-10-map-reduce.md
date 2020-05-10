---
layout: post
title: "Map Reduce"
categories: distributed-systems
date: 2020-05-10 00:00:00
---

MapReduce:

- partitioning input data
- scheduling execution across machines
- handling failures
- inter-machine communication
- fault tolerance
- load balancing

## Worker Failure

The master pings every worker periodically. If no response is received from a worker in a certain amount of time, the master marks the worker as failed. When a map task is executed first by worker A and then later executed by worker B (because A failed), all  workers executing reduce tasks are notified of the reexecution. Any reduce task that has not already read the data from worker A will read the data from worker B.

## Master Failure

It is easy to make the master write periodic checkpoints of the master data structures described above. If the master task dies, a new copy can be started from the last checkpointed state. However, given that there is only a single master, its failure is unlikely. Therefore the implementation aborts the MapReduce computation if the master fails.

## Locality

The MapReduce master takes the location information of the input files into consideration and attempts to schedule a map task on a machine that contains a replica of the corresponding data. Failing that, it attempts to schedule a map task near a replica of that task’s input data. When running large MapReduce operations on a significant fraction of the workers in a cluster, most input data is read locally and consumes no network bandwidth.

