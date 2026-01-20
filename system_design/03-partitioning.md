# Partitioning (Sharding)

> Splitting data across multiple nodes when it's too big for one machine.

---

## Why Partition?

```
┌─────────────────────────────────────────────────────────────────┐
│                     REASONS FOR PARTITIONING                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. SCALABILITY                                                  │
│     └── Data too large for single node                          │
│                                                                  │
│  2. THROUGHPUT                                                   │
│     └── Spread queries across multiple machines                 │
│                                                                  │
│  3. PARALLELISM                                                  │
│     └── Multiple CPUs/disks working simultaneously              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

GOAL: Each partition is a mini-database that can be queried independently
```

---

## Partitioning Strategies

### Strategy 1: Key Range Partitioning

```
Partition data by ranges of the key (like encyclopedia volumes)

┌─────────────────────────────────────────────────────────────────┐
│                         USERS TABLE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Partition 1        Partition 2        Partition 3             │
│   ┌──────────┐      ┌──────────┐      ┌──────────┐             │
│   │ A - G    │      │ H - N    │      │ O - Z    │             │
│   │          │      │          │      │          │             │
│   │ Alice    │      │ Henry    │      │ Oscar    │             │
│   │ Bob      │      │ Ivan     │      │ Peter    │             │
│   │ Carol    │      │ Julia    │      │ Quinn    │             │
│   │ ...      │      │ ...      │      │ ...      │             │
│   └──────────┘      └──────────┘      └──────────┘             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

✅ PROS:
  - Range queries are efficient (all data in few partitions)
  - Keys are sorted within partition
  - Good for time-series: partition by time range

❌ CONS:
  - HOT SPOTS if access patterns are skewed
  - Example: Partitioning by timestamp → all writes hit latest partition
```

### Strategy 2: Hash Partitioning

```
Hash the key, use hash to determine partition

┌─────────────────────────────────────────────────────────────────┐
│                      HASH PARTITIONING                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   hash("Alice") = 42  →  42 mod 3 = 0  →  Partition 0           │
│   hash("Bob")   = 17  →  17 mod 3 = 2  →  Partition 2           │
│   hash("Carol") = 33  →  33 mod 3 = 0  →  Partition 0           │
│   hash("Henry") = 89  →  89 mod 3 = 2  →  Partition 2           │
│                                                                  │
│   Partition 0        Partition 1        Partition 2             │
│   ┌──────────┐      ┌──────────┐      ┌──────────┐             │
│   │ Alice    │      │ David    │      │ Bob      │             │
│   │ Carol    │      │ Frank    │      │ Henry    │             │
│   │ Eve      │      │ Grace    │      │ Ivan     │             │
│   └──────────┘      └──────────┘      └──────────┘             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

✅ PROS:
  - Even distribution (no hot spots from key patterns)
  - Good for point queries

❌ CONS:
  - Range queries are expensive (must query ALL partitions)
  - Lost key ordering
```

### Consistent Hashing

```
PROBLEM WITH SIMPLE HASH:
  - Adding/removing nodes reshuffles EVERYTHING
  - partition = hash(key) mod N
  - Change N → all keys move!


CONSISTENT HASHING:
  - Arrange hash space in a circle (ring)
  - Place nodes at points on the ring
  - Key goes to next node clockwise

                      ┌───────────────┐
                     0│               │
                      │    ◄──Node A  │
                 ────►│               │
               /      │               │
         Node D       │               │      Node B
              ◄───────┤               ├─────►
                      │               │
                      │               │
                      │    Node C──►  │
                      └───────────────┘

Key K: hash(K) lands here ───┘
       Goes to next node clockwise (Node C)


ADDING NODE:
  - New node takes over portion of ring
  - Only neighbors are affected!

                Before              After (add Node E)
              ┌─────────┐          ┌─────────┐
              │    A    │          │  A │ E  │
              │  ┌───┐  │          │┌──┐│┌──┐│
              │  │   │  │   ──►    ││  │││  ││
              │  └───┘  │          │└──┘│└──┘│
              │    B    │          │    B    │
              └─────────┘          └─────────┘

  Only keys in A's range that now fall in E's range need to move
```

### Virtual Nodes (Vnodes)

```
PROBLEM: With few nodes, distribution can be uneven

SOLUTION: Each physical node owns multiple "virtual nodes" on the ring

Physical Node A owns: vnode1, vnode5, vnode9
Physical Node B owns: vnode2, vnode6, vnode10
Physical Node C owns: vnode3, vnode7, vnode11

           Ring with vnodes:
            ┌──────────────┐
            │ v1  v2  v3   │
            │ (A) (B) (C)  │
            │              │
            │ v4  v5  v6   │
            │ (C) (A) (B)  │
            │              │
            │ v7  v8  v9   │
            │ (B) (C) (A)  │
            └──────────────┘

✅ More even distribution
✅ When node fails, load spreads evenly to others
```

---

## Hot Spots and Skewed Workloads

```
PROBLEM: Even with hashing, some keys get way more traffic

Example: Celebrity user with millions of followers
         - user_id = 12345 gets 100x more reads
         - All traffic hits one partition

SOLUTIONS:

1. ADD RANDOM SUFFIX TO HOT KEYS
   ────────────────────────────
   Instead of: user:12345
   Write to:   user:12345:0, user:12345:1, ... user:12345:99

   Writes spread across 100 partitions!

   Reads: Query all 100 keys, merge results
          (trade-off: more complex reads)


2. SPLIT HOT PARTITIONS
   ─────────────────────
   Detect hot partition → split into two
   - Requires monitoring and automation
   - Used by: Spanner, CockroachDB


3. APPLICATION-LEVEL CACHING
   ──────────────────────────
   Cache hot data in front of database
   - Redis, Memcached
   - Reduces load on hot partition
```

---

## Secondary Indexes + Partitioning

Two approaches when you have both partitioning AND secondary indexes:

### Approach 1: Local Index (Document-Partitioned)

```
Each partition maintains its own index for its data

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│   Partition 0               Partition 1               Partition 2│
│   ┌────────────────┐       ┌────────────────┐       ┌──────────┐│
│   │ Data:          │       │ Data:          │       │ Data:    ││
│   │  user:1 (red)  │       │  user:4 (red)  │       │ user:7   ││
│   │  user:2 (blue) │       │  user:5 (blue) │       │ (blue)   ││
│   │  user:3 (red)  │       │  user:6 (red)  │       │ user:8   ││
│   │                │       │                │       │ (red)    ││
│   │ Local Index:   │       │ Local Index:   │       │          ││
│   │  red→[1,3]     │       │  red→[4,6]     │       │ Local:   ││
│   │  blue→[2]      │       │  blue→[5]      │       │ red→[8]  ││
│   └────────────────┘       └────────────────┘       │ blue→[7] ││
│                                                      └──────────┘│
└─────────────────────────────────────────────────────────────────┘

Query: "Find all red users"
  → Must query ALL partitions (scatter-gather)
  → Combine results

✅ Writes are fast (update local index only)
❌ Reads require scatter-gather (query all partitions)
```

### Approach 2: Global Index (Term-Partitioned)

```
Index itself is partitioned separately from data

┌─────────────────────────────────────────────────────────────────┐
│                         DATA PARTITIONS                          │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐            │
│  │ Partition 0│    │ Partition 1│    │ Partition 2│            │
│  │ user:1,2,3 │    │ user:4,5,6 │    │ user:7,8,9 │            │
│  └────────────┘    └────────────┘    └────────────┘            │
│                                                                  │
│                        INDEX PARTITIONS                          │
│  ┌─────────────────────────┐    ┌─────────────────────────┐    │
│  │     Index Partition A    │    │     Index Partition B    │    │
│  │  (colors a-m)            │    │  (colors n-z)            │    │
│  │                          │    │                          │    │
│  │  blue → [2,5,7]          │    │  red → [1,3,4,6,8]       │    │
│  │  green → [...]           │    │  yellow → [...]          │    │
│  └─────────────────────────┘    └─────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

Query: "Find all red users"
  → Query only Index Partition B
  → Get list [1,3,4,6,8]
  → Fetch those specific records

✅ Reads are fast (single index partition)
❌ Writes are slow (must update multiple index partitions)
❌ Index updates often async (eventually consistent)
```

### Comparison

```
┌─────────────────┬─────────────────┬─────────────────┐
│                 │  Local Index    │  Global Index   │
├─────────────────┼─────────────────┼─────────────────┤
│ Write speed     │ Fast            │ Slow            │
│ Read speed      │ Slow (scatter)  │ Fast            │
│ Consistency     │ Strong          │ Often eventual  │
│ Used by         │ MongoDB         │ DynamoDB GSI    │
│                 │ Cassandra       │ Elasticsearch   │
└─────────────────┴─────────────────┴─────────────────┘
```

---

## Rebalancing Partitions

When to rebalance:
- Add nodes (scale out)
- Remove nodes (scale in)
- Node failure
- Uneven load

### Rebalancing Strategies

```
STRATEGY 1: Fixed Number of Partitions
──────────────────────────────────────

Create many partitions upfront (e.g., 1000)
Assign multiple partitions to each node

Adding node: Move some partitions to new node
Removing node: Redistribute its partitions

  Before (3 nodes):          After (add Node D):
  A: [0-333]                 A: [0-250]
  B: [334-666]               B: [251-500]
  C: [667-999]               C: [501-750]
                             D: [751-999]

✅ Only partition assignment changes, not partition boundaries
❌ Must choose partition count upfront (hard to change)

Used by: Elasticsearch, Riak, Couchbase


STRATEGY 2: Dynamic Partitioning
────────────────────────────────

Split partitions when they get too big
Merge partitions when they get too small

  Partition A (10GB) → Split → A1 (5GB) + A2 (5GB)
  Partition B (1GB) + Partition C (1GB) → Merge → BC (2GB)

✅ Adapts to data size
✅ Good for key-range partitioning
❌ Starts with one partition (bottleneck initially)

Used by: HBase, MongoDB


STRATEGY 3: Proportional to Nodes
─────────────────────────────────

Fixed number of partitions PER NODE

3 nodes × 256 partitions/node = 768 total partitions
Add node → 4 nodes × 256 = 1024 partitions

When node joins:
  - Picks random partitions to split
  - Takes half of each

Used by: Cassandra (with consistent hashing)
```

### Automatic vs Manual Rebalancing

```
┌─────────────────────────────────────────────────────────────────┐
│                     ⚠️  WARNING  ⚠️                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Fully automatic rebalancing can be dangerous!                  │
│                                                                  │
│  Scenario:                                                       │
│  1. Node becomes slow (overloaded, not dead)                    │
│  2. System thinks it failed                                     │
│  3. Starts rebalancing → moves data                             │
│  4. Rebalancing overloads other nodes                           │
│  5. Cascade failure!                                            │
│                                                                  │
│  Better: Human approves rebalancing decisions                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Request Routing

How does client know which partition to query?

```
APPROACH 1: Any Node (Gossip)
─────────────────────────────

Client connects to any node
Node routes request to correct partition

┌────────┐     ┌────────┐     ┌────────┐
│Client  │────►│ Any    │────►│ Right  │
│        │     │ Node   │     │ Node   │
└────────┘     └────────┘     └────────┘

Nodes share routing info via gossip protocol
Used by: Cassandra, Riak


APPROACH 2: Routing Tier
────────────────────────

Dedicated routing layer that knows partition map

┌────────┐     ┌────────┐     ┌────────┐
│Client  │────►│ Router │────►│ Right  │
│        │     │(ZooKpr)│     │ Node   │
└────────┘     └────────┘     └────────┘

Router queries coordination service for location
Used by: HBase (ZooKeeper), Kafka


APPROACH 3: Client-Aware
────────────────────────

Client knows partition assignment

┌────────┐
│Client  │──────────────────►│ Right  │
│(smart) │                   │ Node   │
└────────┘

Client caches partition map, refreshes periodically
Used by: MongoDB drivers, Redis Cluster
```

---

## Interview Scenarios

### Scenario 1: "Design a sharding strategy for a social network"

```
Data: Users, Posts, Friendships, Feed

USERS: Hash by user_id
  - Even distribution
  - User profile lookups are fast

POSTS: Hash by user_id (NOT post_id!)
  - All posts by a user on same partition
  - "Get user's posts" is single partition query
  - Trade-off: Can't range query by post_id

FRIENDSHIPS: Shard by user_id
  - Both directions: user_id → [friend_ids]
  - Each user's friends list on one partition

FEED: This is the hard part!
  - Fan-out on write: Write to each follower's feed partition
  - Or fan-out on read: Query all followed users' partitions
  - Hybrid: Fan-out write for normal users, fan-out read for celebrities
```

### Scenario 2: "Hot partition problem - celebrity user"

```
Problem: Taylor Swift has 100M followers
         Every post hammers one partition

Solutions:

1. SPLIT HOT KEY
   - Write to user:taylorswift:0 through user:taylorswift:99
   - Read from all 100, merge

2. SEPARATE HOT DATA
   - Move celebrities to dedicated cluster
   - Special handling with more resources

3. CACHING
   - Cache celebrity content aggressively
   - CDN for media

4. ASYNC FANOUT
   - Don't write to feeds synchronously
   - Queue and process gradually
```

### Scenario 3: "How to add a new shard?"

```
Steps:

1. PROVISION new node

2. COPY data
   - Consistent hashing: New node takes over range
   - Fixed partitions: Move some partitions to new node

3. DUAL WRITE (during transition)
   - Writes go to both old and new location
   - Ensures new node catches up

4. SWITCH READS
   - Start reading from new node
   - Verify correctness

5. STOP DUAL WRITE
   - New node is now authoritative

6. CLEANUP
   - Remove copied data from old nodes

Key: Use coordination service (ZooKeeper) to manage cutover atomically
```

---

## Key Takeaways

```
┌─────────────────────────────────────────────────────────────────┐
│                    REMEMBER FOR INTERVIEWS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Key-range = good for range queries, prone to hot spots      │
│                                                                  │
│  2. Hash = even distribution, no range queries                  │
│                                                                  │
│  3. Consistent hashing minimizes data movement on rebalance     │
│                                                                  │
│  4. Hot spots need special handling (split key, caching)        │
│                                                                  │
│  5. Local index = fast writes, scatter-gather reads             │
│                                                                  │
│  6. Global index = fast reads, slow/async writes                │
│                                                                  │
│  7. Rebalancing should have human oversight                     │
│                                                                  │
│  8. Choose partition key based on access patterns!              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

| Term | One-liner |
|------|-----------|
| **Partition** | Subset of data on one node (aka shard) |
| **Partition key** | Field used to determine which partition |
| **Hot spot** | Partition with disproportionate traffic |
| **Key-range partitioning** | Split by key ranges (sorted) |
| **Hash partitioning** | Split by hash of key (even distribution) |
| **Consistent hashing** | Hash ring that minimizes rebalancing |
| **Virtual nodes** | Multiple points per node on hash ring |
| **Local index** | Each partition indexes its own data |
| **Global index** | Index partitioned separately from data |
| **Scatter-gather** | Query all partitions, combine results |
| **Rebalancing** | Moving data when nodes added/removed |
| **Routing tier** | Service that knows partition locations |
