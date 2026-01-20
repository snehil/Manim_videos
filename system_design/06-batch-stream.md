# Batch & Stream Processing

> Processing large amounts of data, either all at once (batch) or as it arrives (stream).

---

## The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA PROCESSING SPECTRUM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   SERVICES              BATCH                 STREAM             │
│   (Online)              (Offline)             (Near-real-time)   │
│                                                                  │
│   Request/Response      MapReduce             Kafka              │
│   Low latency           High throughput       Continuous         │
│   Wait for result       Run overnight         Minutes/seconds    │
│                                                                  │
│   ◄─────────────────────────────────────────────────────────►   │
│   Seconds               Hours                 Minutes            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Batch Processing

### Unix Philosophy: The Original Batch

```
UNIX PIPES: Simple, composable tools

cat access.log | grep "error" | awk '{print $4}' | sort | uniq -c

Each program:
- Reads from stdin
- Writes to stdout
- Does ONE thing well
- Composable via pipes

┌─────┐    ┌─────┐    ┌─────┐    ┌──────┐    ┌──────┐
│ cat │───►│grep │───►│ awk │───►│ sort │───►│uniq-c│
└─────┘    └─────┘    └─────┘    └──────┘    └──────┘

This works for single machine.
What about terabytes across thousands of machines?
```

---

## MapReduce

```
THE GOOGLE SOLUTION (2004)

Key insight: Distribute Unix philosophy across cluster

INPUT → MAP → SHUFFLE → REDUCE → OUTPUT

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  INPUT FILES                                                     │
│  ┌─────┐ ┌─────┐ ┌─────┐                                        │
│  │File1│ │File2│ │File3│                                        │
│  └──┬──┘ └──┬──┘ └──┬──┘                                        │
│     │       │       │                                            │
│     ▼       ▼       ▼                                            │
│  ┌─────┐ ┌─────┐ ┌─────┐        MAP PHASE                       │
│  │Map 1│ │Map 2│ │Map 3│        (extract key-value pairs)       │
│  └──┬──┘ └──┬──┘ └──┬──┘                                        │
│     │       │       │                                            │
│     └───────┼───────┘                                            │
│             │                                                    │
│     ┌───────┴───────┐           SHUFFLE                         │
│     │ Sort by key   │           (group by key)                  │
│     │ Partition     │                                            │
│     └───────┬───────┘                                            │
│             │                                                    │
│     ┌───────┴───────┐                                            │
│     ▼               ▼                                            │
│  ┌─────┐         ┌─────┐        REDUCE PHASE                    │
│  │Red 1│         │Red 2│        (aggregate values)              │
│  └──┬──┘         └──┬──┘                                        │
│     │               │                                            │
│     ▼               ▼                                            │
│  ┌─────┐         ┌─────┐        OUTPUT FILES                    │
│  │Out 1│         │Out 2│                                        │
│  └─────┘         └─────┘                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### MapReduce Example: Word Count

```
INPUT:
  File 1: "hello world"
  File 2: "hello mapreduce"
  File 3: "world of data"

MAP PHASE (parallel):
  Mapper 1: ("hello", 1), ("world", 1)
  Mapper 2: ("hello", 1), ("mapreduce", 1)
  Mapper 3: ("world", 1), ("of", 1), ("data", 1)

SHUFFLE (by key):
  Partition 1: ("data", [1]), ("hello", [1, 1])
  Partition 2: ("mapreduce", [1]), ("of", [1]), ("world", [1, 1])

REDUCE PHASE (parallel):
  Reducer 1: ("data", 1), ("hello", 2)
  Reducer 2: ("mapreduce", 1), ("of", 1), ("world", 2)

OUTPUT:
  data: 1, hello: 2, mapreduce: 1, of: 1, world: 2
```

### MapReduce Fault Tolerance

```
KEY INSIGHT: Tasks are deterministic and idempotent

If a mapper fails:
  - Reschedule same task on different machine
  - Re-read same input slice
  - Produces same output

If a reducer fails:
  - Re-run reduce task
  - Re-read mapper outputs (stored on disk)

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  WHY IT WORKS:                                                   │
│                                                                  │
│  • Input is immutable (read-only)                               │
│  • Output is written to new files (not in-place update)         │
│  • Tasks have no side effects                                   │
│  • Intermediate results on disk (can re-read)                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Beyond MapReduce

```
MAPREDUCE LIMITATIONS:
  - Intermediate results written to disk (slow)
  - Multi-stage jobs = multiple disk round-trips
  - Batch only (no incremental updates)

MODERN ALTERNATIVES:

SPARK
─────
  - Keep data in memory between stages
  - RDDs (Resilient Distributed Datasets)
  - 10-100x faster than MapReduce for iterative jobs
  - Lazy evaluation, DAG optimization

  val counts = textFile
    .flatMap(line => line.split(" "))
    .map(word => (word, 1))
    .reduceByKey(_ + _)


FLINK
─────
  - True streaming (not micro-batch)
  - Exactly-once semantics
  - Event time processing
  - Used for both batch and stream
```

---

## Data Flows and Joins

### Map-Side Join

```
When one dataset fits in memory

BROADCAST JOIN:
  1. Load small table into memory on each mapper
  2. Stream large table through mapper
  3. Join in memory

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Small table (users)           Large table (clicks)             │
│  ┌─────────────┐               ┌─────────────────┐              │
│  │ user_id │..│               │ user_id │ url   │              │
│  ├─────────────┤               ├─────────────────┤              │
│  │    1    │..│               │    1    │ /home │              │
│  │    2    │..│               │    2    │ /cart │              │
│  │   ...   │..│               │   ...   │  ...  │              │
│  └─────────────┘               └─────────────────┘              │
│        │                               │                        │
│        │ Load into                     │ Stream                 │
│        │ each mapper                   │ through                │
│        ▼                               ▼                        │
│  ┌─────────────────────────────────────────────┐                │
│  │             MAPPER (has users in memory)     │                │
│  │   For each click: lookup user → emit joined │                │
│  └─────────────────────────────────────────────┘                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

✅ No shuffle required
✅ Very fast
❌ Small table must fit in memory
```

### Reduce-Side Join

```
When both datasets are large

SORT-MERGE JOIN:
  1. Mappers emit (join_key, record) from both tables
  2. Shuffle groups by key
  3. Reducer sees all records for each key, joins them

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Users table              Clicks table                          │
│  ┌──────────┐             ┌──────────┐                          │
│  │ Mapper A │             │ Mapper B │                          │
│  └────┬─────┘             └────┬─────┘                          │
│       │                        │                                │
│  (uid=1, user_data)       (uid=1, click_data)                   │
│  (uid=2, user_data)       (uid=1, click_data)                   │
│       │                        │                                │
│       └────────────┬───────────┘                                │
│                    ▼                                            │
│              ┌──────────┐                                       │
│              │ SHUFFLE  │ Group by uid                          │
│              └────┬─────┘                                       │
│                   │                                             │
│                   ▼                                             │
│              ┌──────────┐                                       │
│              │ Reducer  │                                       │
│              │          │                                       │
│              │ uid=1:   │                                       │
│              │  user_data + [click1, click2]                    │
│              └──────────┘                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

✅ Works with any size data
❌ Requires expensive shuffle
```

---

## Stream Processing

```
Process data continuously as it arrives

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  BATCH                           STREAM                         │
│  ─────                           ──────                         │
│                                                                  │
│  Input: Bounded dataset          Input: Unbounded (never ends)  │
│  Output: Complete result         Output: Continuous updates     │
│  Latency: Hours                  Latency: Seconds/minutes       │
│  Failures: Restart from scratch  Failures: Checkpoint & resume  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Kafka: The Backbone

```
WHAT IS KAFKA?

Distributed commit log / message broker

┌─────────────────────────────────────────────────────────────────┐
│                          TOPIC: "clicks"                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Partition 0:  [msg1][msg4][msg7][msg10] ...                    │
│                   ▲                  ▲                           │
│               offset 0           offset 3                        │
│                                                                  │
│  Partition 1:  [msg2][msg5][msg8][msg11] ...                    │
│                                                                  │
│  Partition 2:  [msg3][msg6][msg9][msg12] ...                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

KEY CONCEPTS:
  - Topic: Category of messages
  - Partition: Ordered, immutable sequence
  - Offset: Position within partition
  - Consumer group: Parallelism unit
```

### Kafka Architecture

```
PRODUCERS → BROKERS → CONSUMERS

┌──────────┐      ┌──────────────────────────────┐      ┌──────────┐
│ Producer │─────►│         KAFKA CLUSTER         │─────►│ Consumer │
│    A     │      │  ┌────────┐  ┌────────┐      │      │ Group 1  │
└──────────┘      │  │Broker 1│  │Broker 2│      │      └──────────┘
                  │  │  P0,P1 │  │  P2    │      │
┌──────────┐      │  └────────┘  └────────┘      │      ┌──────────┐
│ Producer │─────►│                              │─────►│ Consumer │
│    B     │      │  Replication factor = 2     │      │ Group 2  │
└──────────┘      │  (each partition on 2 nodes)│      └──────────┘
                  └──────────────────────────────┘

PARTITION ASSIGNMENT:
  - Each partition has one leader broker
  - Writes go to leader, replicated to followers
  - Consumers read from leader (or followers for low latency)
```

### Consumer Groups

```
PARALLELISM VIA PARTITIONS

Rule: Each partition consumed by ONE consumer in a group

┌─────────────────────────────────────────────────────────────────┐
│  Topic with 4 partitions                                         │
│                                                                  │
│  Consumer Group A (2 consumers):                                │
│    Consumer A1: P0, P1                                          │
│    Consumer A2: P2, P3                                          │
│                                                                  │
│  Consumer Group B (4 consumers):                                │
│    Consumer B1: P0                                              │
│    Consumer B2: P1                                              │
│    Consumer B3: P2                                              │
│    Consumer B4: P3                                              │
│                                                                  │
│  Consumer Group C (6 consumers):                                │
│    Consumer C1: P0                                              │
│    Consumer C2: P1                                              │
│    Consumer C3: P2                                              │
│    Consumer C4: P3                                              │
│    Consumer C5: idle (no partition!)                            │
│    Consumer C6: idle                                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

KEY INSIGHT:
  - More partitions = more parallelism
  - Consumers > partitions = some consumers idle
  - Multiple consumer groups = multiple independent subscribers
```

### Kafka vs Traditional Message Queues

```
┌────────────────┬─────────────────────┬─────────────────────┐
│                │ MESSAGE QUEUE       │ KAFKA               │
│                │ (RabbitMQ, SQS)     │                     │
├────────────────┼─────────────────────┼─────────────────────┤
│ Delivery       │ Message deleted     │ Message retained    │
│                │ after consumption   │ (configurable)      │
├────────────────┼─────────────────────┼─────────────────────┤
│ Ordering       │ Best-effort         │ Per-partition       │
├────────────────┼─────────────────────┼─────────────────────┤
│ Replay         │ Not possible        │ Reset offset        │
├────────────────┼─────────────────────┼─────────────────────┤
│ Multi-consumer │ Each message to one │ Each consumer group │
│                │ consumer            │ gets all messages   │
├────────────────┼─────────────────────┼─────────────────────┤
│ Use case       │ Task queues         │ Event streaming,    │
│                │                     │ logs, CDC           │
└────────────────┴─────────────────────┴─────────────────────┘
```

---

## Stream Processing Challenges

### Problem 1: Event Time vs Processing Time

```
EVENT TIME: When the event actually happened
PROCESSING TIME: When we process the event

These are NOT the same!

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Event: User clicked at 10:00:00                                │
│                                                                  │
│  10:00:00 ─────── Network delay ────────► 10:00:05              │
│  (event time)                              (processing time)    │
│                                                                  │
│  Or worse: Mobile app offline, sends events hours later!        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

WHY IT MATTERS:
  "Count events per minute"
  - By processing time: Easy but inaccurate
  - By event time: Accurate but complex (late arrivals!)
```

### Problem 2: Windowing

```
How to group unbounded data for aggregation?

TUMBLING WINDOWS
────────────────
Fixed-size, non-overlapping

  |──── 1min ────|──── 1min ────|──── 1min ────|
  |   window 1   |   window 2   |   window 3   |
  └──────────────┴──────────────┴──────────────►


HOPPING (SLIDING) WINDOWS
─────────────────────────
Fixed-size, overlapping (e.g., 5min window every 1min)

  |────────── 5min ──────────|
       |────────── 5min ──────────|
            |────────── 5min ──────────|
  └──────────────────────────────────────────────►


SESSION WINDOWS
───────────────
Group by activity bursts (gap-based)

  |─ session 1 ─|     |───── session 2 ─────|  |─ s3 ─|
  [events]      gap   [events        events]   gap [events]
  └──────────────────────────────────────────────────────►
```

### Problem 3: Late Arrivals (Watermarks)

```
How do we know when all events for a window have arrived?

WATERMARK: "I believe all events up to time T have arrived"

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Events:    [t=10:00] [t=10:01] [t=10:03] [t=09:59]!            │
│                                              ↑                   │
│                                         Late event!              │
│                                                                  │
│  Watermark at 10:02:                                            │
│    "I've seen 10:02, assuming all ≤10:02 have arrived"          │
│                                                                  │
│  Late event at 09:59:                                           │
│    Options:                                                      │
│    1. Drop it (late data discarded)                             │
│    2. Update window (allowed lateness)                          │
│    3. Emit correction (downstream sees update)                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Trade-off: Wait longer for late data vs higher latency
```

---

## Exactly-Once Semantics

```
THE HOLY GRAIL OF STREAM PROCESSING

Three levels:
  AT-MOST-ONCE:  Message might be lost (fire and forget)
  AT-LEAST-ONCE: Message processed, maybe multiple times
  EXACTLY-ONCE:  Message processed exactly once

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  EXACTLY-ONCE IS HARD BECAUSE:                                  │
│                                                                  │
│  1. Consumer reads message                                       │
│  2. Consumer processes it                                        │
│  3. Consumer commits offset    ← Crash here = reprocess         │
│                                                                  │
│  OR                                                              │
│                                                                  │
│  1. Consumer reads message                                       │
│  2. Consumer commits offset    ← Crash here = lost message      │
│  3. Consumer processes it                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Achieving Exactly-Once

```
OPTION 1: IDEMPOTENT WRITES
───────────────────────────

Process at-least-once, but make writes idempotent
(Same operation multiple times = same result)

  message_id: "abc123"
  Operation: INSERT INTO results (id, value) VALUES ("abc123", 42)
             ON CONFLICT (id) DO NOTHING

  ✅ Simple
  ✅ Works with any sink
  ❌ Requires unique message ID


OPTION 2: TRANSACTIONAL OUTBOX
──────────────────────────────

Write output AND commit offset in same transaction

┌─────────────────────────────────────────────────────────────────┐
│  BEGIN TRANSACTION;                                              │
│    -- Process message and write result                          │
│    INSERT INTO results (value) VALUES (42);                     │
│    -- Record that we've processed this offset                   │
│    UPDATE consumer_offsets SET offset = 100 WHERE topic = 'X';  │
│  COMMIT;                                                         │
└─────────────────────────────────────────────────────────────────┘

  ✅ Truly exactly-once
  ❌ Requires same DB for output and offsets


OPTION 3: KAFKA TRANSACTIONS
────────────────────────────

Kafka supports transactions across topics

  producer.beginTransaction();
  producer.send(record1);
  producer.send(record2);
  producer.sendOffsetsToTransaction(offsets, consumerGroup);
  producer.commitTransaction();

  ✅ Built into Kafka
  ✅ Works across topics
  ❌ Output must be Kafka topic
```

---

## Event Sourcing & CQRS

### Event Sourcing

```
Store EVENTS, not current state

Traditional:
  users table: {id: 1, balance: 150}   ← Only current state

Event Sourcing:
  events table:
    {id: 1, type: "created", balance: 0}
    {id: 1, type: "deposited", amount: 200}
    {id: 1, type: "withdrawn", amount: 50}

  Current state = replay all events

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  BENEFITS:                                                       │
│  • Complete audit trail                                          │
│  • Can replay to any point in time                              │
│  • Debug by replaying events                                    │
│  • Add new views by replaying                                   │
│                                                                  │
│  CHALLENGES:                                                     │
│  • Event schema evolution                                        │
│  • Storage growth                                                │
│  • Eventual consistency                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### CQRS (Command Query Responsibility Segregation)

```
Separate read and write models

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│                         WRITES                                   │
│                           │                                      │
│                           ▼                                      │
│                    ┌─────────────┐                               │
│                    │   COMMAND   │                               │
│                    │    MODEL    │                               │
│                    │  (Events)   │                               │
│                    └──────┬──────┘                               │
│                           │                                      │
│              ┌────────────┼────────────┐                        │
│              │            │            │                        │
│              ▼            ▼            ▼                        │
│        ┌──────────┐ ┌──────────┐ ┌──────────┐                  │
│        │  READ    │ │  READ    │ │  READ    │                  │
│        │ MODEL 1  │ │ MODEL 2  │ │ MODEL 3  │                  │
│        │(Postgres)│ │  (ES)    │ │ (Redis)  │                  │
│        └──────────┘ └──────────┘ └──────────┘                  │
│              │            │            │                        │
│              ▼            ▼            ▼                        │
│           READS        READS        READS                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

WHEN TO USE:
  • Read and write patterns are very different
  • Need multiple read representations
  • Write model is complex (events)
  • High read:write ratio
```

### Change Data Capture (CDC)

```
Stream database changes to other systems

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ┌───────────┐    Read WAL    ┌─────────────┐                  │
│  │ PostgreSQL│───────────────►│   Debezium  │                  │
│  │   (WAL)   │                │    (CDC)    │                  │
│  └───────────┘                └──────┬──────┘                  │
│                                      │                          │
│                                      ▼                          │
│                               ┌─────────────┐                   │
│                               │    KAFKA    │                   │
│                               └──────┬──────┘                   │
│                      ┌───────────────┼───────────────┐         │
│                      ▼               ▼               ▼         │
│               ┌───────────┐   ┌───────────┐   ┌───────────┐   │
│               │Elasticsearch│   │  Redis   │   │  S3/DW    │   │
│               │   (search)  │   │ (cache)  │   │(analytics)│   │
│               └───────────┘   └───────────┘   └───────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

BENEFITS:
  • Keep derived systems in sync
  • No dual-write problem
  • Database is source of truth
  • Async (decoupled)
```

---

## Interview Scenarios

### Scenario 1: "Design a real-time analytics pipeline"

```
Requirements: Count events per minute, handle late data

Architecture:

  Clients → Kafka → Flink/Spark Streaming → Results DB → Dashboard

Design decisions:
  1. Partition Kafka by user_id (ordering within user)
  2. Use event time windowing with watermarks
  3. Allow 5-minute late arrivals
  4. Use exactly-once with idempotent writes (upsert)
  5. Emit window results to time-series DB (InfluxDB, TimescaleDB)

Key points to mention:
  - Event time vs processing time
  - Watermark strategy
  - Late data handling
  - State checkpointing for fault tolerance
```

### Scenario 2: "How does Kafka achieve ordering?"

```
Answer:

1. Ordering is WITHIN partition only
   - Single partition = total order
   - Multiple partitions = no global order

2. Choose partition key wisely
   - Same key → same partition → ordered
   - Example: user_id for user events

3. Producer acks
   - acks=all: Wait for all replicas (stronger durability)
   - Idempotent producer: Prevents duplicates on retry

4. Consumer
   - Read one partition at a time
   - Process in order, commit offset
```

### Scenario 3: "Batch vs Stream - when to use which?"

```
USE BATCH WHEN:
  - Processing historical data
  - Complex analytics (ML training)
  - Result quality > latency
  - Data is naturally bounded (daily logs)
  - Join many datasets

USE STREAM WHEN:
  - Real-time dashboards
  - Alerting/monitoring
  - Low latency requirements
  - Data arrives continuously
  - Need incremental updates

LAMBDA ARCHITECTURE:
  Batch layer (accurate) + Speed layer (fast) + Serving layer

KAPPA ARCHITECTURE:
  Stream only - replay stream for historical
  "Stream processing as unified paradigm"
```

---

## Key Takeaways

```
┌─────────────────────────────────────────────────────────────────┐
│                    REMEMBER FOR INTERVIEWS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. MapReduce: Map (transform) → Shuffle (group) → Reduce (agg) │
│                                                                  │
│  2. Spark keeps data in memory; MapReduce writes to disk        │
│                                                                  │
│  3. Kafka: Distributed log, partitioned, retained                │
│                                                                  │
│  4. Kafka ordering is per-partition only                        │
│                                                                  │
│  5. Event time vs processing time - use watermarks              │
│                                                                  │
│  6. Exactly-once: Idempotent writes or transactional            │
│                                                                  │
│  7. CDC streams database changes to downstream systems          │
│                                                                  │
│  8. Event sourcing: Store events, derive state                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

| Term | One-liner |
|------|-----------|
| **Batch processing** | Process bounded dataset all at once |
| **Stream processing** | Process unbounded data continuously |
| **MapReduce** | Map + Shuffle + Reduce paradigm |
| **Kafka** | Distributed commit log for event streaming |
| **Partition** | Unit of parallelism and ordering in Kafka |
| **Consumer group** | Set of consumers sharing partitions |
| **Offset** | Position in Kafka partition |
| **Watermark** | Progress marker for event time processing |
| **Window** | Time-bounded grouping for aggregation |
| **Exactly-once** | Each message processed exactly once |
| **Idempotent** | Same operation repeated = same result |
| **CDC** | Change Data Capture - stream DB changes |
| **Event sourcing** | Store events as source of truth |
| **CQRS** | Separate read and write models |
