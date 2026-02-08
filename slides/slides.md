# Simulation Factory
## Part 1 — Concurrency as the Control Layer

Async orchestrates work before we make it fast.

---

## Why start with concurrency?

**Simulation Factory problem**

- Many independent jobs
- Each job:
  - Load input (I/O)
  - Run numerical kernel
  - Aggregate & store results
- Jobs have uneven runtimes

**Key idea**

> Before making anything fast, make it *well-orchestrated*.

---

## Concurrency vs Parallelism

### Concurrency
- Multiple tasks *in progress*
- Interleaved execution
- Hides latency
- Often single-threaded

### Parallelism
- Multiple tasks *executing simultaneously*
- Uses multiple cores / devices
- Maximizes throughput

**Rule of thumb**

> Async = *when* things run  
> Parallelism = *where* they run

---

## Why async fits simulation workloads

**Typical job structure**

1. Load data (disk / network)
2. Compute
3. Store results

**Observation**

- I/O dominates wall time
- CPU / GPU often idle
- Runtime varies per job

**Async advantage**

- Overlap I/O and compute
- Keep the pipeline full
- Scale without redesign

---

## Thinking in pipelines

**Pipeline stages**

- Input stage
- Compute stage
- Output stage

**Each stage**
- Runs concurrently
- Communicates via tasks or queues
- Can be scaled independently

**Mental shift**

> Stop writing loops  
> Start designing *flows of work*

---

## Async task orchestration

**Core primitives**

- `async def` — suspendable work
- `await` — explicit yield point
- Tasks — independently scheduled coroutines

**Common patterns**

- Fan-out / fan-in
- Producer / consumer
- Task pools
- Pipelines

**Key property**

> Execution order is explicit and controllable

---

## Structured concurrency

**The problem with ad-hoc tasks**

- Tasks outlive parents
- Exceptions disappear
- Cancellation is unreliable

**Structured concurrency**

- Tasks have a defined lifetime
- Parents wait for children
- Failures propagate correctly

**Model**

> No task escapes its scope

---

## TaskGroup mental model

- Create tasks inside a scope
- Scope exits only when:
  - All tasks finish, or
  - One task fails
- Automatic cleanup on failure

**Result**

- Deterministic behavior
- Easier reasoning
- Fewer leaks

---

## Cancellation is mandatory

**Reality**

- Jobs fail
- Inputs are invalid
- Experiments are stopped

**Async cancellation**

- Cooperative
- Propagates through `await`
- Must be designed in

**Design rule**

> If you can start work, you must be able to stop it.

---

## Backpressure: protecting the system

**Without backpressure**

- Unlimited tasks
- Memory blow-ups
- Device overload
- System collapse

**With backpressure**

- Bounded queues
- Semaphores
- Controlled intake

**Goal**

> Match input rate to processing capacity

---

## Bounded concurrency

**Why limits matter**

- CPU cores are finite
- GPUs saturate
- Memory bandwidth is shared

**Techniques**

- Semaphores
- Fixed-size worker pools
- Stage-specific limits

**Key idea**

> Maximum concurrency ≠ maximum throughput

---

## What we build in Part 1

By the end of this section:

- Async job pipeline
- Structured task lifetimes
- Safe cancellation
- Backpressure & bounded concurrency
- Naive CPU kernel (on purpose)

**Result**

> A correct, scalable control layer

---

## Bridge to Part 2

Next:

- Identify compute hotspots
- Accelerate CPU kernels with Numba
- Keep the async pipeline unchanged

**Narrative thread**

Async orchestrates → Numba accelerates → OpenCL unlocks massive parallelism
