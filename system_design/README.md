# DDIA Interview Notes

> Comprehensive summaries of "Designing Data-Intensive Applications" for system design interviews.

## Quick Navigation

| # | Topic | Key Concepts |
|---|-------|--------------|
| 1 | [Storage Engines](./01-storage-engines.md) | B-Trees, LSM Trees, Indexing |
| 2 | [Replication](./02-replication.md) | Leader-based, Leaderless, Consistency |
| 3 | [Partitioning](./03-partitioning.md) | Sharding strategies, Rebalancing |
| 4 | [Transactions](./04-transactions.md) | ACID, Isolation levels, 2PC |
| 5 | [Consistency & Consensus](./05-consistency-consensus.md) | CAP, Linearizability, Raft |
| 6 | [Batch & Stream Processing](./06-batch-stream.md) | MapReduce, Kafka, Flink |

---

## Interview Cheat Sheet

### When to Use What

```
Need strong consistency?     → Single leader + sync replication
Need high write throughput?  → LSM-tree storage, async replication
Need horizontal scaling?     → Partition/shard the data
Need low latency globally?   → Multi-leader or leaderless + CDN
Need exactly-once?           → Idempotency keys + transactional outbox
```

### Magic Numbers to Remember

| Concept | Number | Why |
|---------|--------|-----|
| Quorum | W + R > N | Guarantees overlap for consistency |
| Typical replication | 3 or 5 nodes | Tolerates 1-2 failures |
| B-tree page size | 4KB | Matches disk/SSD page |
| Kafka partition | 1 consumer/partition | Parallelism unit |

### Red Flags in Design

- Single point of failure (no replication)
- Unbounded queues (memory explosion)
- Sync calls in critical path (latency cascade)
- No idempotency (duplicate processing)
- Global locks (kills scalability)

---

## Study Order for Interviews

**Week 1:** Storage Engines → Replication
**Week 2:** Partitioning → Transactions
**Week 3:** Consistency & Consensus → Batch/Stream

Each topic builds on the previous. Master storage first—it's the foundation.
