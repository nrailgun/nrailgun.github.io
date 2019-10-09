

# Paxos Made Simple

## Introduction

**Paxos** is a family of protocols for **solving consensus** in a network of unreliable processors.

## The Consensus Algorithm

Assume a collection of process that can propose values. A consensus algorithm ensures that a single one among the proposed values is chosen. If a value has been chosen, then processes should be able to learn that chosen value.

### Choosing a Value

Requiring different proposals have different numbers. How this is achieved depends on the implementation.

The algorithm operates in the following 2 phases:

- **Phase 1**
  - A **proposer** selects a proposal number $n$ and sends a **prepare request** with number $n$ to a majority of **acceptor**s.
  - If an acceptor receives a prepare request with a number $n$ greater than any prepare request to which it already responded, then it responds with
    - a promise not to accept any more proposal numbered less $n$, and
    - the highest-numbered proposal (if any) that it has accepted.
- **Phase 2**
  - If the proposer receives a response to its prepare requests (numbered $n$) from a majority of acceptors, then it sends an **accept request** to **each** of those acceptors for a proposal numbered $n$ with a value $v$, where $v$ is the value of the highest-numbered proposalamong the responses, or is any value if the responses reported no proposals.
  - If an acceptor receives an accept request for a proposal numbered $n$, it **accepts** the proposal unless it has already responded to a **prepare request** having a number greater than $n$.

### Learning a Chosen Value

To learn that a value has been chosen, a **learner** must find out that a proposal has been accepted by a majority of acceptors.

1. The obvious algorithm is to have **each** acceptor, whenever it accepts a proposal, respond to **all**
   learners, sending them the proposal. The number responses could be large.
2. We can have the acceptors respond with their acceptances to a **distinguished learner**,
   which in turn informs the other learners when a value has been chosen. It is also less reliable, since the distinguished learner could fail.

The failure of an acceptor could make it impossible to know whether a majority had accepted a particular proposal. If a learner needs to know whether a value has been chosen, it can have a
proposer issue a proposal.

### Progress

It’s easy to construct a scenario in which two proposers each keep issuing a sequence of proposals with increasing numbers, none of which are ever chosen. To **guarantee progress**, a **distinguished proposer** (some sort of leader) must be selected as the only one to try issuing proposals. 

The famous result of *F. L. P* implies that a reliable algorithm for electing a proposer must use either randomness or real time.

Anyway, *this paper didn't give any detail about how the distinguished proposer is selected*.