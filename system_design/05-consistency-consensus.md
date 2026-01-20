# Consistency & Consensus

> How distributed systems agree on shared state and what guarantees they provide.

---

## The Fundamental Problem

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE DISTRIBUTED SYSTEMS PROBLEM               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  In a distributed system:                                        │
│                                                                  │
│  • Networks can lose, delay, or reorder messages                │
│  • Nodes can crash or be slow                                   │
│  • Clocks are never perfectly synchronized                       │
│                                                                  │
│  Yet we need nodes to AGREE on things:                          │
│  • Who is the leader?                                           │
│  • What value was committed?                                    │
│  • Who holds the lock?                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Consistency Models

From strongest to weakest guarantees:

```
STRONGEST
    │
    ▼
┌─────────────────────────────────────┐
│         LINEARIZABILITY             │  "As if one copy"
│   (Strong/Atomic Consistency)       │  Real-time ordering
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│      SEQUENTIAL CONSISTENCY         │  Global order exists
│                                     │  Not real-time
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│       CAUSAL CONSISTENCY            │  Cause → Effect
│                                     │  preserved
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│      EVENTUAL CONSISTENCY           │  Will converge
│                                     │  Eventually...
└─────────────────────────────────────┘
    │
    ▼
WEAKEST
```

---

## Linearizability (Strong Consistency)

```
THE GOLD STANDARD

System behaves as if there's only ONE copy of the data
Every operation takes effect atomically at some point between
its invocation and completion.

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Real time ────────────────────────────────────────────────►    │
│                                                                  │
│  Client A:  ├───write(x=1)───┤                                  │
│                        ↓                                         │
│                   (takes effect here)                            │
│                        ↓                                         │
│  Client B:        ├───read(x)───┤ → must return 1               │
│                                                                  │
│  If B's read STARTS after A's write ENDS,                       │
│  B must see A's write.                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Linearizability Examples

```
LINEARIZABLE (VALID):
─────────────────────

Timeline:
  Client A: ├──write(1)──┤
  Client B:              ├──read──┤ → 1  ✓
  Client C:                    ├──read──┤ → 1  ✓

Write finishes, all subsequent reads see it.


NOT LINEARIZABLE (INVALID):
───────────────────────────

Timeline:
  Client A: ├──write(1)──┤
  Client B:              ├──read──┤ → 1  ✓
  Client C:                    ├──read──┤ → 0  ✗

C's read starts after B saw 1, but C sees old value.
This is NOT linearizable (time went "backwards").
```

### When You Need Linearizability

```
1. LEADER ELECTION
   ─────────────────
   Must agree on exactly one leader
   "Is there a leader? Who is it?"
   If not linearizable: Split brain!

2. DISTRIBUTED LOCKS
   ──────────────────
   Only one client holds lock at a time
   If not linearizable: Multiple holders!

3. UNIQUE CONSTRAINTS
   ───────────────────
   Two users can't claim same username
   If not linearizable: Duplicates possible!

4. CROSS-CHANNEL COORDINATION
   ───────────────────────────
   Example: Upload image → send message with URL
   If not linearizable: Message arrives before image is visible
```

### How to Implement Linearizability

```
OPTION 1: Single Leader
────────────────────────
All reads and writes go to leader
Leader serializes all operations

✅ Simple
❌ Leader is bottleneck and SPOF


OPTION 2: Consensus Algorithm (Raft, Paxos)
───────────────────────────────────────────
Get majority agreement on each operation
Each operation gets a slot in the log

✅ Fault tolerant
❌ Slower (multiple round trips)


OPTION 3: Linearizable Quorums (sort of)
────────────────────────────────────────
Leaderless with strict quorum + read repair

⚠️ Cassandra/Dynamo quorums are NOT linearizable
   (due to sloppy quorums, LWW, etc.)
```

### The Cost of Linearizability

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERFORMANCE IMPACT                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Linearizable read: Must check with majority                    │
│                     OR read from leader                         │
│                     → Network round trip(s)                     │
│                                                                  │
│  Linearizable write: Must replicate synchronously               │
│                      → Wait for majority acknowledgment         │
│                                                                  │
│  Result: Higher latency, especially across datacenters          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## CAP Theorem

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│               C ──────────────── A                              │
│                \               /                                │
│                 \             /                                 │
│                  \           /                                  │
│                   \         /                                   │
│                    \       /                                    │
│                     \     /                                     │
│                      \   /                                      │
│                       \ /                                       │
│                        P                                        │
│                                                                  │
│  C = Consistency (linearizability)                              │
│  A = Availability (every request gets response)                 │
│  P = Partition tolerance (system works despite network splits)  │
│                                                                  │
│  THE THEOREM: During a network partition, you must choose       │
│               between C and A. You can't have both.             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### CAP in Practice

```
Network partition happens:

                    PARTITION
                       ║
    ┌─────────┐        ║        ┌─────────┐
    │ Node A  │        ║        │ Node B  │
    │         │◄───────╳───────►│         │
    └─────────┘        ║        └─────────┘
                       ║
    Clients here               Clients here


CHOICE 1: CP (Consistent, Partition-tolerant)
─────────────────────────────────────────────
- Nodes on minority side refuse to serve requests
- System partially unavailable
- But no inconsistent data

Examples: ZooKeeper, etcd, Consul, HBase


CHOICE 2: AP (Available, Partition-tolerant)
────────────────────────────────────────────
- Both sides continue serving requests
- May return stale data
- Risk of conflicts when partition heals

Examples: Cassandra, CouchDB, DynamoDB
```

### PACELC: A Better Framework

```
CAP only talks about partition scenarios. What about normal operation?

PACELC:

  If PARTITION:
    Choose Availability or Consistency (A or C)

  Else (normal operation):
    Choose Latency or Consistency (L or C)


┌─────────────┬─────────────────┬─────────────────┐
│   System    │  If Partition   │    Else         │
├─────────────┼─────────────────┼─────────────────┤
│ Cassandra   │ A (available)   │ L (low latency) │
│ DynamoDB    │ A               │ L              │
│ PostgreSQL  │ C (consistent)  │ C              │
│ ZooKeeper   │ C               │ C              │
│ Spanner     │ C               │ C              │
└─────────────┴─────────────────┴─────────────────┘
```

---

## Causal Consistency

```
Weaker than linearizability, stronger than eventual

GUARANTEE: If operation A causally precedes B, everyone sees A before B

┌─────────────────────────────────────────────────────────────────┐
│                     CAUSALITY EXAMPLES                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  A causes B if:                                                  │
│  • Same client: A happens before B                              │
│  • B reads value written by A                                   │
│  • Transitivity: A→B and B→C means A→C                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

EXAMPLE:

  Alice posts: "How much is 1+1?"
  Bob replies: "2"

  CAUSAL: Bob's reply depends on Alice's question
          Everyone must see question before answer

  NOT CAUSAL: Alice changes profile photo
              Bob likes a different post
              (Independent - can be seen in any order)
```

### Implementing Causal Consistency

```
LAMPORT TIMESTAMPS
──────────────────

Each node has a counter
On send: increment counter, attach to message
On receive: counter = max(local, received) + 1

  Node A          Node B          Node C
  ──────          ──────          ──────
  [1]────send────►[2]
                  [2]────send────►[3]
                       ◄──send────[3]
                  [4]

Provides total order, but doesn't capture all causality


VECTOR CLOCKS
─────────────

Track counter for EACH node: [A:1, B:2, C:0]

  Node A starts: [A:1, B:0, C:0]
  A sends to B:  B receives, now [A:1, B:1, C:0]

  Can detect: "Did A happen before B?"
  Compare vectors element-wise

  [A:1, B:2] happened before [A:2, B:3]  ✓
  [A:1, B:2] vs [A:2, B:1]  → CONCURRENT (neither before other)

Used by: Riak, Dynamo (for conflict detection)
```

---

## Consensus Algorithms

```
THE CONSENSUS PROBLEM:

Multiple nodes must agree on a value, even if some fail.

Requirements:
1. AGREEMENT: All non-faulty nodes decide same value
2. VALIDITY: Decided value was proposed by someone
3. TERMINATION: Eventually a decision is made
4. INTEGRITY: Each node decides at most once
```

### Raft: The Understandable Consensus

```
RAFT OVERVIEW
─────────────

Three states: Follower, Candidate, Leader

Normal operation:
  ┌──────────────────────────────────────────────┐
  │                                              │
  │  ┌────────┐         ┌────────┐              │
  │  │Follower│◄────────│ Leader │              │
  │  └────────┘  heart  └────┬───┘              │
  │       ▲      beat        │                  │
  │       │                  │                  │
  │  ┌────┴───┐              │                  │
  │  │Follower│◄─────────────┘                  │
  │  └────────┘   replicate                     │
  │                                              │
  └──────────────────────────────────────────────┘
```

### Raft: Leader Election

```
1. TIMEOUT
   Follower doesn't hear from leader
   → Becomes Candidate

2. REQUEST VOTES
   Candidate asks all nodes for votes
   Includes: term number, last log entry

3. VOTE
   Nodes vote for first candidate they hear from
   (if candidate's log is at least as up-to-date)

4. WIN
   Candidate gets majority → becomes Leader
   Tells everyone "I'm the leader for term N"


TIMELINE:

  Leader dies
       │
       ▼
  ┌────────┐ timeout ┌──────────┐ votes ┌────────┐
  │Follower│────────►│Candidate │──────►│ Leader │
  └────────┘         └──────────┘       └────────┘
                           │
                           │ loses election
                           ▼
                     ┌────────┐
                     │Follower│
                     └────────┘
```

### Raft: Log Replication

```
1. Client sends command to Leader
2. Leader appends to its log
3. Leader sends AppendEntries to all followers
4. Followers append to their logs, acknowledge
5. Once majority acknowledge → entry is COMMITTED
6. Leader responds to client
7. Leader tells followers to apply committed entries

┌─────────────────────────────────────────────────────────────────┐
│                           LEADER LOG                             │
├─────────────────────────────────────────────────────────────────┤
│  [1:set x=5] [2:set y=7] [3:set x=9] [4:set z=2]               │
│      ▲                                    ▲                      │
│      │                                    │                      │
│  committed                            uncommitted                │
│  (applied)                            (waiting for              │
│                                        majority)                 │
└─────────────────────────────────────────────────────────────────┘

FOLLOWER LOGS:

  Follower A: [1:set x=5] [2:set y=7] [3:set x=9]  ✓ caught up
  Follower B: [1:set x=5] [2:set y=7]              lagging
  Follower C: [1:set x=5] [2:set y=7] [3:set x=9]  ✓ caught up

  Entry 3 committed: 3 of 4 nodes have it (majority)
```

### Raft Safety Rules

```
1. ELECTION SAFETY
   At most one leader per term

2. LEADER APPEND-ONLY
   Leader never overwrites/deletes its own log

3. LOG MATCHING
   If two logs have entry with same index and term,
   all preceding entries are identical

4. LEADER COMPLETENESS
   If entry is committed, it will be present in all
   future leaders' logs

5. STATE MACHINE SAFETY
   If server applies entry at index, no other server
   applies different entry at that index
```

---

## Distributed Coordination Services

```
ZooKeeper, etcd, Consul: Implementations of consensus for practical use

WHAT THEY PROVIDE:
──────────────────

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  1. LINEARIZABLE KEY-VALUE STORE                                │
│     Small config data, not general-purpose DB                   │
│                                                                  │
│  2. LEADER ELECTION                                             │
│     "Who is the current leader of service X?"                   │
│                                                                  │
│  3. DISTRIBUTED LOCKS                                           │
│     Acquire/release locks across nodes                          │
│                                                                  │
│  4. SERVICE DISCOVERY                                           │
│     "What nodes are currently part of cluster Y?"               │
│                                                                  │
│  5. WATCHES/NOTIFICATIONS                                       │
│     "Tell me when this value changes"                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Leader Election with ZooKeeper

```
PATTERN: Ephemeral sequential nodes

1. Each candidate creates /election/node- (ephemeral, sequential)
   → ZK assigns: /election/node-0001, /election/node-0002, etc.

2. Check: "Am I the lowest number?"
   YES → I'm the leader
   NO  → Watch the node just below me

3. If node I'm watching disappears → repeat step 2

WHY EPHEMERAL?
  If leader crashes, its session ends
  ZK deletes ephemeral node automatically
  Next in line becomes leader

┌─────────────────────────────────────────────────────────────────┐
│ /election/                                                       │
│   ├── node-0001 (ephemeral) ← LEADER                            │
│   ├── node-0002 (ephemeral) ← watching 0001                     │
│   └── node-0003 (ephemeral) ← watching 0002                     │
└─────────────────────────────────────────────────────────────────┘
```

### Fencing Tokens

```
PROBLEM: Leader thinks it's still leader after pause

  Leader A: Acquires lock
            │
            │ Long GC pause / network delay
            │
            │ Lock expires (times out)
            │
  Leader B: Acquires same lock
            │
            ▼ Writes to storage
            │
  Leader A: Wakes up, thinks it has lock
            │
            ▼ Also writes to storage  ← CONFLICT!


SOLUTION: Fencing tokens

Lock service returns monotonically increasing token:
  A gets lock with token 33
  B gets lock with token 34

Storage checks: "Is this token >= last seen?"
  A writes with token 33 ← Rejected! (34 was seen)
  B writes with token 34 ← Accepted

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Lock with token 33          Lock with token 34                 │
│         │                            │                          │
│         ▼                            ▼                          │
│  ┌──────────────────────────────────────────┐                   │
│  │              STORAGE                      │                   │
│  │  last_token = 34                          │                   │
│  │  Reject writes with token < 34            │                   │
│  └──────────────────────────────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Byzantine Fault Tolerance (BFT)

```
So far: Assumed nodes are HONEST (fail-stop)
        Either working correctly or crashed

BYZANTINE FAULTS: Nodes can LIE
  - Send different values to different nodes
  - Collude with other malicious nodes
  - Bug causing corrupted data

BYZANTINE GENERALS PROBLEM:
  Generals surrounding a city
  Must agree: Attack or Retreat
  Some generals might be traitors

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  With f Byzantine nodes, need:                                  │
│  • 3f + 1 total nodes (to tolerate f failures)                  │
│  • Example: 4 nodes can tolerate 1 Byzantine node               │
│                                                                  │
│  Much more expensive than crash fault tolerance!                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

USED IN:
  - Blockchain (Bitcoin, Ethereum)
  - Airplane flight computers
  - Nuclear control systems

NOT typically used in datacenter systems:
  - Trust your own hardware
  - Crash faults are much more common
  - BFT is expensive
```

---

## Interview Scenarios

### Scenario 1: "Explain CAP Theorem"

```
Framework:

1. Define the three properties:
   - Consistency: Linearizability (every read sees most recent write)
   - Availability: Every request gets a response
   - Partition tolerance: System operates despite network failures

2. The theorem:
   "During a network partition, you must choose between C and A"

3. Give examples:
   - CP: ZooKeeper, etcd (refuse requests during partition)
   - AP: Cassandra, DynamoDB (serve stale data during partition)

4. Nuance:
   - "It's not a binary choice - it's a spectrum"
   - "CAP only applies during partitions"
   - "PACELC is more complete: latency vs consistency in normal operation"
```

### Scenario 2: "How does Raft work?"

```
Answer structure:

1. HIGH LEVEL:
   "Raft elects a leader who coordinates all writes.
    Log entries are replicated to majority before committing."

2. LEADER ELECTION:
   - Terms (logical clock)
   - Candidate requests votes
   - Majority wins
   - Only one leader per term

3. LOG REPLICATION:
   - Leader appends entry
   - Sends to followers
   - Committed when majority have it
   - Applied to state machine

4. SAFETY:
   - Leader has all committed entries
   - Followers only vote for candidates with complete log
```

### Scenario 3: "When do you need consensus?"

```
Answer:

Use consensus when you need:
1. Leader election (exactly one leader)
2. Distributed locks (mutual exclusion)
3. Atomic transactions (all-or-nothing)
4. Unique ID generation
5. Critical configuration changes

Don't use consensus for:
1. High-volume reads (use caching)
2. Data that can be eventually consistent
3. Operations that can be retried safely
4. Independent data that doesn't need coordination
```

---

## Key Takeaways

```
┌─────────────────────────────────────────────────────────────────┐
│                    REMEMBER FOR INTERVIEWS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Linearizability = "as if one copy" with real-time ordering  │
│                                                                  │
│  2. CAP: During partition, choose Consistency or Availability   │
│                                                                  │
│  3. PACELC: Even without partition, choose Latency or Consistency│
│                                                                  │
│  4. Causal consistency: preserves cause→effect order            │
│                                                                  │
│  5. Raft: Leader election + log replication + majority commit   │
│                                                                  │
│  6. ZooKeeper/etcd: Consensus as a service (locks, election)    │
│                                                                  │
│  7. Fencing tokens prevent "zombie leaders"                     │
│                                                                  │
│  8. Byzantine = nodes can lie; need 3f+1 nodes for f failures   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

| Term | One-liner |
|------|-----------|
| **Linearizability** | Operations appear atomic and in real-time order |
| **Sequential consistency** | Global order exists but not real-time |
| **Causal consistency** | Cause-effect ordering preserved |
| **Eventual consistency** | Will converge... eventually |
| **CAP theorem** | Partition → choose Consistency or Availability |
| **PACELC** | Adds Latency vs Consistency during normal operation |
| **Consensus** | Multiple nodes agreeing on a value |
| **Raft** | Leader-based consensus algorithm |
| **Paxos** | Original (complex) consensus algorithm |
| **Term** | Logical time period in Raft |
| **Quorum** | Majority needed for consensus |
| **Fencing token** | Monotonic token to prevent stale leader writes |
| **Byzantine fault** | Node actively lying/corrupting |
