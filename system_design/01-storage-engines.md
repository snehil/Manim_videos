# Storage Engines

> How databases store and retrieve data. This is foundational—understand this first.

---

## The Big Picture

Every database needs to answer: **How do we store data so we can find it quickly?**

Two dominant approaches:

```
┌─────────────────────────────────────────────────────────────────┐
│                     STORAGE ENGINE SPECTRUM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   B-TREE                                          LSM-TREE      │
│   ◄──────────────────────────────────────────────────────────►  │
│                                                                  │
│   • Read-optimized                        • Write-optimized     │
│   • In-place updates                      • Append-only         │
│   • PostgreSQL, MySQL                     • Cassandra, RocksDB  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## B-Trees

### How It Works

B-trees break data into fixed-size **pages** (typically 4KB) organized as a tree.

```
                         ┌─────────────────┐
                         │   [30] [60]     │  ◄── Root Page
                         └────┬─────┬──────┘
                  ┌───────────┘     └───────────┐
                  ▼                             ▼
         ┌────────────────┐            ┌────────────────┐
         │  [10] [20]     │            │  [40] [50]     │  ◄── Internal Pages
         └──┬─────┬───────┘            └──┬─────┬───────┘
            │     │                       │     │
    ┌───────┘     └────┐          ┌───────┘     └────┐
    ▼                  ▼          ▼                  ▼
┌────────┐      ┌────────┐   ┌────────┐       ┌────────┐
│ Data   │      │ Data   │   │ Data   │       │ Data   │  ◄── Leaf Pages
│ 1-9    │      │ 11-19  │   │ 31-39  │       │ 41-49  │      (actual rows)
└────────┘      └────────┘   └────────┘       └────────┘
```

### Write Operation

```
Writing key=15:

1. Start at root
2. 15 < 30, go left
3. 10 < 15 < 20, go to middle child
4. Found leaf page → UPDATE IN PLACE
5. Write-ahead log (WAL) for durability

┌─────────────────────────────────────────────────────┐
│ IMPORTANT: In-place update = need locks for safety  │
└─────────────────────────────────────────────────────┘
```

### Key Properties

| Property | Value | Interview Tip |
|----------|-------|---------------|
| Depth | O(log n) | ~4 levels for millions of rows |
| Page size | 4KB typical | Matches SSD/disk page |
| Branching factor | ~500 | Each page holds many keys |
| Reads | O(log n) | Very fast |
| Writes | O(log n) | But requires locking |

### When to Use B-Trees

✅ Read-heavy workloads
✅ Need range queries (`WHERE age BETWEEN 20 AND 30`)
✅ Need strong consistency (transactions)
✅ Traditional RDBMS (PostgreSQL, MySQL InnoDB)

---

## LSM Trees (Log-Structured Merge Trees)

### How It Works

Never modify data in place. Always append, then merge in background.

```
                    WRITES
                       │
                       ▼
              ┌─────────────────┐
              │    MEMTABLE     │  ◄── In-memory, sorted (Red-Black tree)
              │   (few MBs)     │
              └────────┬────────┘
                       │ Flush when full
                       ▼
              ┌─────────────────┐
              │   SSTable L0    │  ◄── Immutable sorted files on disk
              ├─────────────────┤
              │   SSTable L0    │
              └────────┬────────┘
                       │ Compaction (merge + dedupe)
                       ▼
              ┌─────────────────┐
              │   SSTable L1    │  ◄── Larger, merged files
              ├─────────────────┤
              │   SSTable L1    │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   SSTable L2    │  ◄── Even larger
              └─────────────────┘
```

### Write Path

```
Write (key=42, value="hello"):

1. Append to WAL (durability)        ──► Sequential write (FAST!)
2. Insert into Memtable (sorted)     ──► In-memory (FAST!)
3. Done! Return to client

Background:
4. Memtable full → flush to SSTable
5. Too many SSTables → compact & merge
```

### Read Path

```
Read (key=42):

1. Check Memtable                    ──► Found? Return
2. Check Bloom filters for SSTables  ──► Skip SSTables that definitely don't have it
3. Check SSTables L0 → L1 → L2...    ──► Most recent first
4. Return value (or not found)

┌─────────────────────────────────────────────────────────────┐
│ Reads can be slower! May need to check multiple SSTables   │
└─────────────────────────────────────────────────────────────┘
```

### Bloom Filters (Critical for LSM reads)

```
Bloom Filter: Probabilistic "maybe yes, definitely no" structure

┌──────────────────────────────────────────────────────┐
│ "Is key=42 in this SSTable?"                         │
│                                                      │
│   Bloom filter says NO  → Definitely not there       │
│   Bloom filter says YES → Might be there, check file │
└──────────────────────────────────────────────────────┘

Space: ~10 bits per key = 1% false positive rate
```

### Compaction Strategies

```
SIZE-TIERED (default in Cassandra)
─────────────────────────────────
- Merge SSTables of similar size
- Good for write-heavy
- Can use lots of disk space temporarily

LEVELED (default in RocksDB)
────────────────────────────
- Each level is 10x larger than previous
- Better read performance
- More consistent disk usage
- Higher write amplification
```

### Write Amplification

```
The same data gets written multiple times:

Original write → Memtable → L0 → L1 → L2 → L3
     1x           1x        1x    1x    1x    1x = 6x write amplification!

┌─────────────────────────────────────────────────────────────┐
│ Trade-off: LSM has write amplification but sequential I/O  │
│            B-tree has random I/O but writes data once      │
└─────────────────────────────────────────────────────────────┘
```

### When to Use LSM Trees

✅ Write-heavy workloads
✅ Time-series data (always appending)
✅ Need high write throughput
✅ Cassandra, RocksDB, LevelDB, HBase

---

## Head-to-Head Comparison

```
                    B-TREE              LSM-TREE
                    ──────              ────────
Write pattern       Random I/O          Sequential I/O
Read pattern        Single seek         Multiple seeks (maybe)
Write speed         Moderate            Fast
Read speed          Fast                Moderate
Space usage         More fragmentation  Compaction overhead
Concurrency         Needs locking       Lock-free writes
Use case            OLTP, transactions  Time-series, logs

```

| Aspect | B-Tree | LSM-Tree |
|--------|--------|----------|
| **Write** | Slower (random I/O, locks) | Faster (sequential, append-only) |
| **Read** | Faster (one location) | Slower (multiple SSTables) |
| **Space** | Fragmentation | Temporary bloat during compaction |
| **Predictability** | Consistent | Compaction can cause latency spikes |

---

## Indexing

### Primary vs Secondary Index

```
PRIMARY INDEX (clustered)
──────────────────────────
Data is STORED in index order

┌─────────────────────────────────┐
│ PK │ Name    │ Age │ City      │
├────┼─────────┼─────┼───────────┤
│ 1  │ Alice   │ 30  │ NYC       │  ◄── Rows stored sorted by PK
│ 2  │ Bob     │ 25  │ LA        │
│ 3  │ Charlie │ 35  │ Chicago   │
└────┴─────────┴─────┴───────────┘


SECONDARY INDEX (non-clustered)
───────────────────────────────
Index points TO the data location

Age Index:                         Heap File:
┌─────┬────────┐                  ┌───────────────┐
│ 25  │ row 2  │─────────────────►│ Bob, 25, LA   │
│ 30  │ row 1  │─────────────────►│ Alice, 30, NYC│
│ 35  │ row 3  │─────────────────►│ Charlie, 35.. │
└─────┴────────┘                  └───────────────┘
```

### Index Types

```
COVERING INDEX (Index-only scan)
────────────────────────────────
Store extra columns IN the index to avoid heap lookup

CREATE INDEX idx ON users(email) INCLUDE (name, created_at);

Query: SELECT name FROM users WHERE email = 'x@y.com'
→ Answered entirely from index! No heap access.


COMPOSITE INDEX
───────────────
Multiple columns, ORDER MATTERS!

CREATE INDEX idx ON orders(customer_id, order_date);

✅ WHERE customer_id = 5                    (uses index)
✅ WHERE customer_id = 5 AND order_date > X (uses index)
❌ WHERE order_date > X                      (can't use index!)

Think of it like a phone book: sorted by (last_name, first_name)
Can find all "Smiths" but can't efficiently find all "Johns"


HASH INDEX
──────────
O(1) lookup, no range queries

┌─────────────────────────────────────────┐
│ hash("alice@email.com") → bucket 42     │
│ bucket 42 → row pointer                 │
└─────────────────────────────────────────┘

✅ Exact match: WHERE email = 'x@y.com'
❌ Range: WHERE email > 'a' (useless)
```

---

## Interview Scenarios

### Scenario 1: "Design a time-series database"

```
Answer: LSM-tree based storage

Why:
- Writes are append-only (perfect for LSM)
- Data is naturally sorted by time
- High write throughput needed
- Reads are often range scans (recent data)

Example: InfluxDB, TimescaleDB uses LSM-inspired storage
```

### Scenario 2: "Why is my query slow?"

```
Checklist:
1. Is there an index? → EXPLAIN ANALYZE
2. Is the index being used? → Check query planner
3. Index type matches query?
   - Range query on hash index = bad
   - Composite index in wrong order = bad
4. Too many rows returned? → Index can't help with large result sets
5. Need covering index? → Avoid heap lookups
```

### Scenario 3: "How does PostgreSQL differ from Cassandra?"

```
PostgreSQL (B-tree):
- Strong consistency, ACID transactions
- Read-optimized
- Single node by default
- Use for: OLTP, complex queries, joins

Cassandra (LSM-tree):
- Eventual consistency
- Write-optimized
- Distributed by design
- Use for: High write throughput, time-series, logs
```

---

## Key Takeaways

```
┌─────────────────────────────────────────────────────────────────┐
│                    REMEMBER FOR INTERVIEWS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. B-tree = read-optimized, random I/O, in-place updates       │
│                                                                  │
│  2. LSM-tree = write-optimized, sequential I/O, append-only     │
│                                                                  │
│  3. LSM uses Bloom filters to speed up reads                    │
│                                                                  │
│  4. Write amplification is the cost of LSM trees                │
│                                                                  │
│  5. Index order matters for composite indexes                   │
│                                                                  │
│  6. Covering indexes avoid heap lookups                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

| Term | One-liner |
|------|-----------|
| **WAL** | Write-ahead log for durability before confirming write |
| **Memtable** | In-memory sorted structure in LSM |
| **SSTable** | Sorted String Table - immutable sorted file on disk |
| **Compaction** | Background merge of SSTables |
| **Bloom filter** | Probabilistic structure: "definitely no" or "maybe yes" |
| **Write amplification** | Data written multiple times due to compaction |
| **Covering index** | Index contains all columns needed for query |
| **Clustered index** | Data stored in index order |
