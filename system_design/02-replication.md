# Replication

> Keeping copies of data on multiple machines for fault tolerance and performance.

---

## Why Replicate?

```
┌─────────────────────────────────────────────────────────────────┐
│                    REASONS FOR REPLICATION                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. HIGH AVAILABILITY                                            │
│     └── System keeps working when nodes fail                     │
│                                                                  │
│  2. FAULT TOLERANCE                                              │
│     └── No single point of failure                               │
│                                                                  │
│  3. LATENCY                                                      │
│     └── Serve reads from geographically closer replica           │
│                                                                  │
│  4. READ SCALABILITY                                             │
│     └── Spread read load across replicas                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Three Replication Models

```
┌────────────────┐    ┌────────────────┐    ┌────────────────┐
│ SINGLE-LEADER  │    │  MULTI-LEADER  │    │   LEADERLESS   │
├────────────────┤    ├────────────────┤    ├────────────────┤
│                │    │                │    │                │
│    ┌───┐       │    │  ┌───┐ ┌───┐  │    │  ┌───┐ ┌───┐  │
│    │ L │       │    │  │ L │ │ L │  │    │  │ N │ │ N │  │
│    └─┬─┘       │    │  └─┬─┘ └─┬─┘  │    │  └───┘ └───┘  │
│   ┌──┴──┐      │    │    │  ╳  │    │    │      ╳ ╳      │
│   ▼     ▼      │    │    ▼     ▼    │    │  ┌───┐ ┌───┐  │
│ ┌───┐ ┌───┐    │    │  ┌───┐ ┌───┐  │    │  │ N │ │ N │  │
│ │ F │ │ F │    │    │  │ F │ │ F │  │    │  └───┘ └───┘  │
│ └───┘ └───┘    │    │  └───┘ └───┘  │    │               │
│                │    │                │    │ All nodes are │
│ PostgreSQL     │    │ Multi-DC setup │    │    equal      │
│ MySQL          │    │ CRDTs          │    │               │
│ MongoDB        │    │                │    │ Cassandra     │
│                │    │                │    │ DynamoDB      │
└────────────────┘    └────────────────┘    └────────────────┘
```

---

## Single-Leader Replication

### How It Works

```
          WRITES                              READS
            │                              ┌────┴────┐
            ▼                              ▼         ▼
       ┌─────────┐                    ┌─────────┐  ┌─────────┐
       │ LEADER  │───replication────► │FOLLOWER │  │FOLLOWER │
       │ (write) │                    │ (read)  │  │ (read)  │
       └─────────┘                    └─────────┘  └─────────┘
            │
            └───────────────────────────────────┐
                                                ▼
                                           ┌─────────┐
                                           │FOLLOWER │
                                           │ (read)  │
                                           └─────────┘

All writes go to leader → Leader streams changes to followers
```

### Sync vs Async Replication

```
SYNCHRONOUS
───────────

Client ──write──► Leader ──replicate──► Follower
                    │                       │
                    │◄────── ACK ───────────┘
                    │
                 ACK to client

✅ Guaranteed durability (data on 2+ nodes)
❌ Slow (wait for follower)
❌ Unavailable if follower is down


ASYNCHRONOUS
────────────

Client ──write──► Leader ──ACK──► Client
                    │
                    └──replicate──► Follower (eventually)

✅ Fast writes
✅ Leader doesn't block
❌ Data loss possible if leader dies before replication
❌ Replication lag issues


SEMI-SYNCHRONOUS (Practical choice)
───────────────────────────────────

- 1 follower is sync (guaranteed backup)
- Other followers are async (performance)
- If sync follower fails, promote another to sync
```

### Replication Lag Problems

When followers fall behind the leader, clients see inconsistent data:

```
PROBLEM 1: Read Your Own Writes
────────────────────────────────

Timeline:
  User writes "name=Bob"    Leader has "Bob"
         │                        │
         │                   lag──┼──lag
         │                        │
  User reads name           Follower still has "Alice"
         │
         └──► User sees "Alice"!  WTF?


SOLUTION: Read-your-writes consistency
  - Read from leader for recently modified data
  - Track last write timestamp, only read from up-to-date replicas
  - Sticky sessions (same user → same replica)
```

```
PROBLEM 2: Monotonic Reads
──────────────────────────

Timeline:
  User reads from Follower A    → sees comment
  User reads from Follower B    → comment gone! (B is behind)
  User reads from Follower A    → sees comment again

  User thinks: "Am I going crazy?"


SOLUTION: Monotonic reads
  - Each user always reads from same replica
  - Hash user_id to replica
```

```
PROBLEM 3: Consistent Prefix Reads
──────────────────────────────────

Imagine chat messages with causality:

  Alice: "How much is 1+1?"   (written first)
  Bob: "2"                    (written second, causally depends on Alice)

If replicated out of order:
  Observer sees: Bob: "2"
                 Alice: "How much is 1+1?"

  "2" before the question? Makes no sense!


SOLUTION: Consistent prefix reads
  - Causally related writes go to same partition
  - Use logical timestamps / vector clocks
```

### Failover

```
WHAT HAPPENS WHEN LEADER DIES?

1. DETECT FAILURE
   └── Heartbeat timeout (typically 30s)

2. CHOOSE NEW LEADER
   └── Election (Raft) or designated by controller
   └── Usually: replica with most up-to-date data

3. RECONFIGURE SYSTEM
   └── Clients redirect writes to new leader
   └── Old leader (if recovers) becomes follower


FAILOVER PROBLEMS:

┌─────────────────────────────────────────────────────────────────┐
│ SPLIT BRAIN                                                     │
│ ────────────                                                    │
│ Two nodes both think they're the leader                         │
│ → Both accept writes → Data diverges → Disaster                 │
│                                                                  │
│ Solution: Fencing (STONITH - Shoot The Other Node In The Head)  │
│           Only one can acquire the lease/lock                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ LOST WRITES                                                     │
│ ───────────                                                     │
│ New leader might be behind old leader                           │
│ → Unreplicated writes are lost                                  │
│                                                                  │
│ Solution: Accept data loss OR use sync replication              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Multi-Leader Replication

### When to Use

```
USE CASE 1: Multi-datacenter
─────────────────────────────

        US-EAST                          EU-WEST
     ┌─────────────┐                 ┌─────────────┐
     │   Leader    │◄───async sync──►│   Leader    │
     │   ┌───┐     │                 │     ┌───┐   │
     │   │ L │     │                 │     │ L │   │
     │   └───┘     │                 │     └───┘   │
     │    │        │                 │      │      │
     │    ▼        │                 │      ▼      │
     │ Followers   │                 │  Followers  │
     └─────────────┘                 └─────────────┘

- Local writes = low latency
- Cross-DC replication = async (tolerate DC failure)


USE CASE 2: Offline-capable apps
─────────────────────────────────

Phone (leader) ◄──── sync when online ────► Server (leader)

Each device is a "datacenter" that can work offline
```

### The Big Problem: Write Conflicts

```
CONFLICT EXAMPLE:
─────────────────

User A in US:  UPDATE title = "ABC"   at time T1
User B in EU:  UPDATE title = "XYZ"   at time T1 (same time!)

Both succeed locally. When they sync:

     US Leader                    EU Leader
    title="ABC"  ◄──conflict!──► title="XYZ"

Which one wins?
```

### Conflict Resolution Strategies

```
1. LAST WRITE WINS (LWW)
────────────────────────
   - Attach timestamp to each write
   - Highest timestamp wins
   - Simple but LOSES DATA

   ┌─────────────────────────────────────────────┐
   │ Cassandra uses this. Beware of clock skew!  │
   └─────────────────────────────────────────────┘


2. MERGE VALUES
───────────────
   - Combine both values: "ABC" + "XYZ" = "ABC, XYZ"
   - Works for some data types (sets, lists)


3. CUSTOM RESOLUTION
────────────────────
   - App-specific logic
   - Example: Keep edit with most characters
   - Example: Prompt user to resolve


4. CRDTs (Conflict-free Replicated Data Types)
──────────────────────────────────────────────
   - Data structures designed for automatic merge
   - G-Counter, LWW-Register, OR-Set
   - Mathematically guaranteed to converge

   Example: G-Counter (Grow-only counter)
   ┌─────────────────────────────────────┐
   │ Node A: {A: 5, B: 0}                │
   │ Node B: {A: 0, B: 3}                │
   │ Merged: {A: 5, B: 3} → total = 8    │
   └─────────────────────────────────────┘
```

---

## Leaderless Replication

### How It Works

```
No leader! Client writes to multiple nodes directly.

                    CLIENT
                   /   |   \
                  /    |    \
                 ▼     ▼     ▼
              ┌───┐ ┌───┐ ┌───┐
              │ A │ │ B │ │ C │
              └───┘ └───┘ └───┘

Write: Send to ALL nodes
Read:  Query MULTIPLE nodes, take most recent
```

### Quorums

```
N = total nodes
W = write acknowledgments required
R = read nodes queried

RULE: W + R > N  →  Guaranteed to see latest write

Example: N=3, W=2, R=2

WRITE (need 2 ACKs):
  Client ──write──► Node A ✓
         ──write──► Node B ✓  ◄── Got 2 ACKs, success!
         ──write──► Node C ✗  (timeout/failed)

READ (query 2 nodes):
  Client ──read──► Node A  → version 5
         ──read──► Node C  → version 4
                            └── Return version 5 (latest)

W=2, R=2: At least one node has latest value
```

### Common Quorum Configurations

```
┌─────────┬───────┬───────┬───────┬─────────────────────────────┐
│ Config  │   N   │   W   │   R   │ Trade-off                   │
├─────────┼───────┼───────┼───────┼─────────────────────────────┤
│ Default │   3   │   2   │   2   │ Balanced                    │
│ Fast W  │   3   │   1   │   3   │ Fast writes, slow reads     │
│ Fast R  │   3   │   3   │   1   │ Slow writes, fast reads     │
│ Strong  │   3   │   3   │   3   │ Slowest, strongest          │
└─────────┴───────┴───────┴───────┴─────────────────────────────┘
```

### Read Repair & Anti-Entropy

```
READ REPAIR
───────────
During read, if stale replica detected → update it

Client reads from A, B, C
  A: version 5
  B: version 5
  C: version 4  ◄── Stale!

Client sends version 5 to C → C now up-to-date


ANTI-ENTROPY
────────────
Background process compares replicas and syncs differences
Uses Merkle trees for efficient comparison
```

### Sloppy Quorums & Hinted Handoff

```
PROBLEM: What if W nodes are unavailable?

Normal quorum: Write fails (can't reach W nodes)

SLOPPY QUORUM: Write to ANY available nodes
               → Higher availability
               → Weaker consistency guarantee


HINTED HANDOFF
──────────────

Node A is down. Write intended for A goes to Node D (temporary).

  Client ──write──► Node D (holding hint for A)

When A recovers:
  Node D ──handoff──► Node A (here's what you missed)
  Node D deletes the hint

┌─────────────────────────────────────────────────────────────┐
│ With sloppy quorum, W + R > N doesn't guarantee consistency │
│ Because W might not include the "right" nodes               │
└─────────────────────────────────────────────────────────────┘
```

---

## Comparison Table

```
┌────────────────┬────────────────┬────────────────┬────────────────┐
│                │ Single-Leader  │ Multi-Leader   │ Leaderless     │
├────────────────┼────────────────┼────────────────┼────────────────┤
│ Write latency  │ Depends on     │ Low (local     │ Depends on W   │
│                │ sync/async     │ leader)        │                │
├────────────────┼────────────────┼────────────────┼────────────────┤
│ Consistency    │ Strong (sync)  │ Eventual       │ Tunable        │
│                │ Eventual(async)│                │ (quorum)       │
├────────────────┼────────────────┼────────────────┼────────────────┤
│ Conflicts      │ None           │ Yes (resolve)  │ Yes (versioning│
│                │                │                │ /LWW)          │
├────────────────┼────────────────┼────────────────┼────────────────┤
│ Availability   │ Leader is SPOF │ High           │ High           │
├────────────────┼────────────────┼────────────────┼────────────────┤
│ Complexity     │ Simple         │ Complex        │ Moderate       │
├────────────────┼────────────────┼────────────────┼────────────────┤
│ Examples       │ PostgreSQL     │ CockroachDB    │ Cassandra      │
│                │ MySQL          │                │ DynamoDB       │
│                │ MongoDB        │                │ Riak           │
└────────────────┴────────────────┴────────────────┴────────────────┘
```

---

## Interview Scenarios

### Scenario 1: "How would you handle a database failover?"

```
Answer framework:

1. DETECTION
   - Heartbeat monitoring
   - Consensus-based detection (avoid false positives)

2. ELECTION
   - Raft/Paxos for leader election
   - Choose most up-to-date replica

3. RECONFIGURATION
   - Update DNS/load balancer
   - Old leader fenced (prevent split-brain)

4. RECOVERY
   - New leader catches up followers
   - Old leader rejoins as follower

Key concerns:
- Data loss from unreplicated writes
- Split-brain prevention
- Connection draining
```

### Scenario 2: "Design a globally distributed database"

```
Consider:
- Multi-leader for low latency writes in each region
- OR Leaderless with geographically-aware quorums

Trade-offs:
- Strong consistency → single leader (high latency)
- Low latency → multi-leader/leaderless (conflict resolution)
- Read scalability → add read replicas

Mention: CockroachDB, Spanner, Cassandra approaches
```

### Scenario 3: "User reports seeing stale data after updating profile"

```
Diagnosis: Replication lag + reading from follower

Solutions:
1. Read-your-writes consistency
   - Read from leader for 10s after write
   - Or track write timestamp in session

2. Sticky sessions
   - Route same user to same replica

3. Wait for replication
   - After write, wait until follower confirms

4. Client-side: Version/ETag checking
```

---

## Key Takeaways

```
┌─────────────────────────────────────────────────────────────────┐
│                    REMEMBER FOR INTERVIEWS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Single-leader is simplest but leader is a bottleneck/SPOF   │
│                                                                  │
│  2. Sync replication = durability, Async = performance          │
│                                                                  │
│  3. Replication lag causes read-your-writes, monotonic read,    │
│     and consistent prefix issues                                │
│                                                                  │
│  4. Multi-leader has write conflicts → need resolution strategy │
│                                                                  │
│  5. Leaderless uses quorums: W + R > N for consistency          │
│                                                                  │
│  6. Sloppy quorum trades consistency for availability           │
│                                                                  │
│  7. Split-brain is the nightmare scenario → use fencing         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

| Term | One-liner |
|------|-----------|
| **Replica** | Copy of data on another node |
| **Leader** | Node that accepts writes |
| **Follower** | Node that copies leader's writes |
| **Sync replication** | Wait for follower ACK before confirming |
| **Async replication** | Confirm immediately, replicate in background |
| **Failover** | Promote follower to leader when leader dies |
| **Split-brain** | Two nodes both think they're leader |
| **Quorum** | Minimum nodes for read/write to succeed |
| **Read repair** | Fix stale replica during read |
| **Hinted handoff** | Temporarily store data for unavailable node |
| **LWW** | Last-write-wins conflict resolution |
| **CRDT** | Data structure that auto-merges without conflicts |
