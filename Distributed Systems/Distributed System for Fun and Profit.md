## Basics

### Goals

- Scalability
  - Size
  - Geographic
  - Administrative
- Performance (Lantency)
  - Short response
  - High throughput
  - Low utilization of computing resource(s)
- Availability
- Latency
- Fault Tolerance

What prevent us from achieving goals?

- Increased probability of failure.
- Increased communication among nodes
- Increased communication latency (due to increased geographic distance)

### Abstraction and Models

- system model
  - asynchronous
  - synchronous
- failure model
  - crash-fail
  - partitions
  - byzatine
- consistency model
  - strong
  - eventual

### Partition and Replicate

Partitioning is dividing the dataset into smaller distinct independent sets; this is used to reduce the impact of dataset growth since each partition is a subset of the data. Partitioning is also very much application specific.

Replication is making copies of the same data on multiple machines; this allows more servers to take part in the computation.

## Up and Down the Level of Abstraction

Implications:

- each node executes concurrently.
- knowledge is local (maybe out-dated).
- nodes can fail and recover independently.
- messages can be delayed or lost.
- clocks are not synchronized.

### The Consensus Problem

The **consensus problem** requires agreement among a number of processes (or agents) for a single data value.

- Agreement
- Integrity
- Termination
- Validity

### 2 Impossibilities

- FLP Impossibility Result

CAP Theorem

- (Strong) consistency
- Availability
- Partition Tolerance

Many early system distributed relational database systems did not take into account partition tolerance. Partition tolerance is important for modern systems since network partitions become much more likely if the system is geographically distributed.

