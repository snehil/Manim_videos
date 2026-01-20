# Transactions

> Grouping operations so they succeed or fail together, with isolation from concurrent operations.

---

## ACID: The Four Guarantees

```
┌─────────────────────────────────────────────────────────────────┐
│                           A C I D                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ATOMICITY                                                       │
│  └── All or nothing. If any part fails, entire txn rolls back.  │
│                                                                  │
│  CONSISTENCY                                                     │
│  └── App invariants are maintained. (Actually app's job, not DB)│
│                                                                  │
│  ISOLATION                                                       │
│  └── Concurrent txns don't interfere with each other.           │
│                                                                  │
│  DURABILITY                                                      │
│  └── Once committed, data survives crashes.                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Atomicity in Practice

```
TRANSFER $100 FROM ALICE TO BOB:

BEGIN TRANSACTION;
  UPDATE accounts SET balance = balance - 100 WHERE user = 'Alice';
  UPDATE accounts SET balance = balance + 100 WHERE user = 'Bob';
COMMIT;

Without atomicity:
  - First update succeeds
  - Crash!
  - Alice lost $100, Bob didn't get it

With atomicity:
  - Crash → Both updates rolled back
  - Money is safe
```

### Durability: How It Works

```
WRITE-AHEAD LOG (WAL)
─────────────────────

Before modifying data:
1. Write change to log (sequential, fast)
2. Flush log to disk
3. Acknowledge commit
4. Eventually apply to actual data pages

On crash:
- Replay log to recover committed transactions
- Uncommitted transactions are rolled back

┌────────────────────────────────────────────────────┐
│ Log is sequential → Fast writes                    │
│ Data pages are random access → Updated lazily      │
└────────────────────────────────────────────────────┘
```

---

## Isolation Levels

The most asked topic! Know this cold.

```
┌─────────────────────────────────────────────────────────────────┐
│              ISOLATION LEVEL SPECTRUM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Read              Snapshot          Serializable                │
│  Uncommitted       Isolation         ───────────►               │
│  ◄─────────────────────────────────────────────────────────────►│
│                                                                  │
│  Weakest                                             Strongest   │
│  Fastest                                             Slowest     │
│  Most anomalies                                      No anomalies│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Read Phenomena (Anomalies)

```
DIRTY READ
──────────
Reading uncommitted data from another transaction

  Txn A                    Txn B
  ─────                    ─────
  UPDATE x = 100
                           SELECT x → sees 100 (uncommitted!)
  ROLLBACK (x back to 50)
                           Uses 100... but it was never committed!


DIRTY WRITE
───────────
Overwriting uncommitted data from another transaction

  Txn A                    Txn B
  ─────                    ─────
  UPDATE x = 100
                           UPDATE x = 200 (overwrites uncommitted)
  COMMIT
                           ROLLBACK (x = ??? undefined state)


NON-REPEATABLE READ
───────────────────
Same query returns different results within same transaction

  Txn A                    Txn B
  ─────                    ─────
  SELECT x → 50
                           UPDATE x = 100
                           COMMIT
  SELECT x → 100           Different result!


PHANTOM READ
────────────
New rows appear/disappear in a range query

  Txn A                    Txn B
  ─────                    ─────
  SELECT COUNT(*) WHERE age > 25 → 5 rows
                           INSERT (age=30)
                           COMMIT
  SELECT COUNT(*) WHERE age > 25 → 6 rows  (phantom!)


WRITE SKEW
──────────
Two transactions read same data, make decisions, write different rows

  Example: Hospital requires at least 1 doctor on call

  Txn A (Alice)            Txn B (Bob)
  ─────────────            ───────────
  SELECT COUNT(*) WHERE on_call = true → 2 (Alice & Bob)
                           SELECT COUNT(*) WHERE on_call = true → 2
  "OK, 2 doctors, I can leave"
                           "OK, 2 doctors, I can leave"
  UPDATE Alice SET on_call = false
                           UPDATE Bob SET on_call = false
  COMMIT                   COMMIT

  Result: NO doctors on call! Invariant violated.
```

### Isolation Levels Explained

```
┌──────────────────┬────────────┬─────────────┬─────────────┬───────────┐
│ Isolation Level  │ Dirty Read │ Non-repeat  │ Phantom     │ Write Skew│
├──────────────────┼────────────┼─────────────┼─────────────┼───────────┤
│ Read Uncommitted │ Possible   │ Possible    │ Possible    │ Possible  │
│ Read Committed   │ Prevented  │ Possible    │ Possible    │ Possible  │
│ Repeatable Read  │ Prevented  │ Prevented   │ Possible    │ Possible  │
│ Snapshot (MVCC)  │ Prevented  │ Prevented   │ Prevented*  │ Possible  │
│ Serializable     │ Prevented  │ Prevented   │ Prevented   │ Prevented │
└──────────────────┴────────────┴─────────────┴─────────────┴───────────┘
* Snapshot isolation prevents phantom reads but not write skew
```

---

## Read Committed

```
Most common default level (PostgreSQL, SQL Server)

GUARANTEES:
1. No dirty reads - only see committed data
2. No dirty writes - only overwrite committed data

HOW IT WORKS:
- Writes: Hold row-level lock until commit
- Reads: Read latest committed value (no lock)

┌─────────────────────────────────────────────────────┐
│ Simple implementation:                              │
│ - Track committed version of each row               │
│ - Readers see committed version only                │
│ - Writers acquire lock, release on commit           │
└─────────────────────────────────────────────────────┘
```

---

## Snapshot Isolation (MVCC)

```
See a consistent snapshot of the database at transaction start

IMPLEMENTATION: Multi-Version Concurrency Control (MVCC)

Each row has multiple versions with transaction IDs:

┌──────────────────────────────────────────────────────────────┐
│ Row: user Alice                                              │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ Version 1 │ created_by: txn 100 │ deleted_by: txn 150  │   │
│ │           │ balance: 500        │                      │   │
│ ├───────────┼─────────────────────┼──────────────────────┤   │
│ │ Version 2 │ created_by: txn 150 │ deleted_by: txn 200  │   │
│ │           │ balance: 600        │                      │   │
│ ├───────────┼─────────────────────┼──────────────────────┤   │
│ │ Version 3 │ created_by: txn 200 │ deleted_by: NULL     │   │
│ │           │ balance: 750        │ (current)            │   │
│ └───────────┴─────────────────────┴──────────────────────┘   │
└──────────────────────────────────────────────────────────────┘

Transaction 175 starts:
  - Can see: Version 2 (created by 150 < 175, not yet deleted)
  - Cannot see: Version 3 (created by 200 > 175)
```

### MVCC Visibility Rules

```
Transaction T can see a row version if:

1. created_by transaction is committed AND created_by < T
2. deleted_by is NULL OR deleted_by > T OR deleted_by is not committed

In plain English:
- See versions from transactions that started before you
- Don't see versions from transactions that started after you
- Don't see uncommitted changes
```

### Snapshot Isolation Visualized

```
Timeline:

Txn 100 ──────[commit]
Txn 150 ──────────────[commit]
Txn 175 ──────[START]───────────────────────────[queries]──────
Txn 200 ──────────────────────[commit]

Txn 175's snapshot:
- Sees state as of when 175 started
- Includes changes from 100, 150 (committed before 175)
- Excludes changes from 200 (committed after 175 started)
- Consistent view throughout entire transaction!
```

---

## Write Skew & How to Prevent It

```
WRITE SKEW: The anomaly snapshot isolation doesn't prevent

Two transactions:
1. Read overlapping data
2. Make decisions based on that read
3. Write to DIFFERENT rows
4. Both commit → invariant violated

The problem: No write conflict detected (different rows!)
```

### Solutions to Write Skew

```
SOLUTION 1: SELECT FOR UPDATE
─────────────────────────────

Explicitly lock the rows you're basing your decision on

BEGIN TRANSACTION;
  SELECT * FROM doctors
  WHERE on_call = true
  FOR UPDATE;  ← Locks these rows!

  -- Check count, decide to leave
  UPDATE doctors SET on_call = false WHERE name = 'Alice';
COMMIT;

Other transaction blocks on FOR UPDATE until first commits


SOLUTION 2: Materializing Conflicts
───────────────────────────────────

Create a row that represents the thing you're protecting

Instead of checking count of doctors:
- Create a "shift" row for each time slot
- Lock the shift row

BEGIN;
  SELECT * FROM shifts WHERE date = '2024-01-15' FOR UPDATE;
  -- Now update the doctor
COMMIT;


SOLUTION 3: Serializable Isolation
──────────────────────────────────

Use true serializable isolation (see next section)
Database automatically detects and prevents write skew
```

---

## Serializable Isolation

The gold standard. Transactions behave as if they ran one at a time.

### Implementation 1: Actual Serial Execution

```
Literally run transactions one at a time on single thread

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Transaction Queue:  [Txn A] → [Txn B] → [Txn C] → ...          │
│                          ↓                                       │
│                    Single Thread                                 │
│                    Executes One                                  │
│                    At A Time                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

✅ Simple, truly serializable
✅ No locks needed
❌ Limited throughput (single core)
❌ Transactions must be fast (no waiting for network)

Used by: Redis, VoltDB

KEY INSIGHT: Works because:
- RAM is fast (no disk I/O waiting)
- Transactions are stored procedures (no client round-trips)
```

### Implementation 2: Two-Phase Locking (2PL)

```
Pessimistic concurrency control: Lock everything you touch

TWO PHASES:
1. GROWING PHASE: Acquire locks, never release
2. SHRINKING PHASE: Release all locks (at commit/abort)

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Txn A: [acquire X lock]──[acquire Y lock]──[COMMIT: release]   │
│                                                                  │
│                              │                                   │
│  Txn B: ──────[wants X]──────┼──[BLOCKED]───[gets X after A]    │
│                              │                                   │
│                          A holds X                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

LOCK TYPES:
- Shared (S): For reading, multiple allowed
- Exclusive (X): For writing, only one

Lock compatibility:
          S     X
     S   ✓     ✗
     X   ✗     ✗

PROBLEM: Deadlocks!

  Txn A holds X, wants Y
  Txn B holds Y, wants X
  → Both blocked forever

Solution: Deadlock detection → abort one transaction
```

### Implementation 3: Serializable Snapshot Isolation (SSI)

```
Optimistic: Execute transactions, detect conflicts, abort if needed

Based on snapshot isolation + conflict detection

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  1. Transaction runs on snapshot (like normal MVCC)              │
│  2. Track what was read                                          │
│  3. At commit: Check if any read data was modified              │
│  4. If conflict detected → abort and retry                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Conflict detection for write skew:

Txn A reads doctors (2 on call)    Txn B reads doctors (2 on call)
         ↓                                    ↓
  Writes Alice off-call              Writes Bob off-call
         ↓                                    ↓
       Commit                        Tries to commit
                                             ↓
                              SSI detects: "You read doctors,
                              but Txn A modified it"
                                             ↓
                                      ABORT Txn B

✅ Better performance than 2PL (no blocking)
✅ Prevents write skew (unlike plain snapshot)
❌ May abort transactions (retry overhead)

Used by: PostgreSQL (SERIALIZABLE), CockroachDB
```

### Comparison

```
┌─────────────────┬────────────────┬─────────────────┬──────────────┐
│                 │ Serial         │ 2PL             │ SSI          │
├─────────────────┼────────────────┼─────────────────┼──────────────┤
│ Concurrency     │ None           │ Limited         │ High         │
│ Throughput      │ CPU-bound      │ Lock contention │ Good         │
│ Latency         │ Low            │ Can be high     │ Low          │
│ Deadlocks       │ No             │ Yes             │ No           │
│ Aborts          │ No             │ On deadlock     │ On conflict  │
│ Best for        │ RAM DBs        │ General         │ General      │
└─────────────────┴────────────────┴─────────────────┴──────────────┘
```

---

## Distributed Transactions

When transactions span multiple databases/services.

### Two-Phase Commit (2PC)

```
Coordinate commit across multiple nodes

PARTICIPANTS: Multiple databases/services
COORDINATOR: Single node that drives the protocol

PHASE 1: PREPARE
────────────────
                    ┌───────────────┐
                    │  Coordinator  │
                    └───────┬───────┘
                   prepare  │  prepare
               ┌────────────┼────────────┐
               ▼            ▼            ▼
          ┌────────┐   ┌────────┐   ┌────────┐
          │ Node A │   │ Node B │   │ Node C │
          └────┬───┘   └────┬───┘   └────┬───┘
               │            │            │
            YES/NO       YES/NO       YES/NO
               │            │            │
               └────────────┼────────────┘
                            ▼
                    ┌───────────────┐
                    │  Coordinator  │
                    └───────────────┘

"Can you commit?"
Nodes: Write to log, lock resources, respond YES or NO


PHASE 2: COMMIT/ABORT
─────────────────────

If ALL said YES:
  Coordinator: "COMMIT"
  All nodes: Commit and release locks

If ANY said NO (or timeout):
  Coordinator: "ABORT"
  All nodes: Rollback and release locks
```

### 2PC Problems

```
PROBLEM 1: Coordinator Failure
──────────────────────────────

After PREPARE, before COMMIT decision:
- Participants are stuck holding locks
- Can't commit (don't know decision)
- Can't abort (coordinator might have decided commit)
- Blocked until coordinator recovers!

                ┌───────────────┐
                │  Coordinator  │
                │    💀 DEAD    │
                └───────────────┘

          ┌────────┐   ┌────────┐
          │ Node A │   │ Node B │
          │PREPARED│   │PREPARED│
          │BLOCKED │   │BLOCKED │
          └────────┘   └────────┘


PROBLEM 2: Performance
──────────────────────

- Multiple round trips
- Locks held across network calls
- Any slow participant slows everyone
- Doesn't scale well


SOLUTION: 3PC, Paxos Commit, or Saga pattern
```

### Saga Pattern (Alternative to 2PC)

```
For long-running transactions across services

Instead of locking everything:
1. Execute each step with local transaction
2. If any step fails, execute COMPENSATING transactions

EXAMPLE: Book a trip (flight + hotel + car)

Forward path:
  Book Flight → Book Hotel → Book Car
       ↓            ↓           ↓
   Reserved     Reserved    Reserved

If Car fails:
  Cancel Hotel → Cancel Flight
       ↓              ↓
   Refunded       Refunded


┌─────────────────────────────────────────────────────────────────┐
│ SAGA PROPERTIES:                                                 │
│                                                                  │
│ ✅ No distributed locks (better availability)                   │
│ ✅ Each step is local transaction                               │
│ ❌ Not truly atomic (intermediate states visible)               │
│ ❌ Compensating transactions can be complex                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Interview Scenarios

### Scenario 1: "Explain isolation levels"

```
Framework for answering:

1. Start with READ COMMITTED (most common default)
   - Prevents dirty reads/writes
   - Still has non-repeatable reads

2. Move to SNAPSHOT ISOLATION
   - Uses MVCC
   - Consistent view of data
   - But: write skew is possible

3. End with SERIALIZABLE
   - Gold standard
   - Three implementations: serial, 2PL, SSI
   - Trade-off: performance

Key phrase: "It's a spectrum of trade-offs between
             consistency guarantees and performance"
```

### Scenario 2: "What is write skew?"

```
Answer:

1. Define it:
   "Two transactions read overlapping data, make decisions,
    then write to different rows. Both commit, but combined
    effect violates an invariant."

2. Give example:
   - Doctor on-call example
   - Two doctors both go off-call because each saw 2 doctors

3. How to prevent:
   - SELECT FOR UPDATE (explicit locking)
   - Serializable isolation
   - Materializing conflicts (create lock row)
```

### Scenario 3: "When would you use 2PC?"

```
Answer:

When you need:
- Atomic commits across multiple databases
- Can't tolerate partial success

Examples:
- Banking: Transfer between two banks
- Order system: Inventory + Payment together

But mention drawbacks:
- Coordinator is SPOF
- Poor performance (locks held across network)
- Participants block if coordinator fails

Alternatives:
- Saga pattern for long-running processes
- Eventual consistency with compensation
- Single database if possible!
```

---

## Key Takeaways

```
┌─────────────────────────────────────────────────────────────────┐
│                    REMEMBER FOR INTERVIEWS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. ACID: Atomicity (all-or-nothing), Isolation (no interference)│
│     Durability (survives crashes). C is app's job.              │
│                                                                  │
│  2. Read Committed prevents dirty reads but allows phantoms     │
│                                                                  │
│  3. Snapshot isolation (MVCC) gives consistent view but allows  │
│     write skew                                                   │
│                                                                  │
│  4. Write skew = read same data, decide, write different rows   │
│     Fix: SELECT FOR UPDATE or serializable                      │
│                                                                  │
│  5. Serializable: Serial execution, 2PL, or SSI                 │
│                                                                  │
│  6. 2PC coordinates distributed commits but coordinator is SPOF │
│                                                                  │
│  7. Saga pattern: Local txns + compensating actions             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

| Term | One-liner |
|------|-----------|
| **ACID** | Atomicity, Consistency, Isolation, Durability |
| **WAL** | Write-ahead log for crash recovery |
| **Dirty read** | Reading uncommitted data |
| **Non-repeatable read** | Same query, different results |
| **Phantom** | New rows appear in range query |
| **Write skew** | Concurrent decisions on shared read data |
| **MVCC** | Multi-version concurrency control |
| **2PL** | Two-phase locking (growing + shrinking) |
| **SSI** | Serializable snapshot isolation (optimistic) |
| **2PC** | Two-phase commit for distributed txns |
| **Saga** | Sequence of local txns + compensating actions |
| **SELECT FOR UPDATE** | Explicit lock on read rows |
