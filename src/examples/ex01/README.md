# Exercise 01 — Async Food-Truck Factory

This exercise introduces **concurrency as the control layer** using Python’s
`asyncio` library.

You are given a simple async pipeline that models a food-truck kitchen:

Producer → ingredients → cook → prepare → Customer


Each stage:
- runs concurrently
- communicates via `asyncio.Queue`
- processes one order at a time

The goal is **not to make things faster**, but to make the system
**well-orchestrated**.

You must use **only the Python standard library (`asyncio`)**.

---

## Learning Objectives

By completing this exercise, you should be able to:

- Explain how async pipelines work
- Understand backpressure and bottlenecks
- Scale a system using concurrency
- Reason about shutdown and robustness in async programs

---

## Task 1 — Add Backpressure 🛑

**Goal:** See how queues control the flow of work.

### What to do

Change all queues to have a small maximum size, for example:
  ```python
  asyncio.Queue(maxsize=1)
  ```


## Key concept
Backpressure via bounded queues.

## Task 2 — Scale a Bottleneck Stage 🔥
**Goal:** Improve throughput without changing the pipeline structure.

### What to do
Identify the slowest stage (hint: cook) and create two instances of that stage.
Both instances should read from the same input queue write to the same output queue

## Key concept
Competing consumers and horizontal scaling.

<!-- Observe
Orders complete faster.
Output from different workers interleaves. -->

## Task 3 — Handle Slow or Stuck Orders ⏱️
**Goal:** Prevent a single slow order from blocking the pipeline.

### What to do
Wrap the stage work in a timeout using:

```python
asyncio.wait_for(...)
```
If the timeout expires:

mark the order as failed

forward status to the next stage!

<!-- Observe
The pipeline continues processing other orders.

Failures do not stall the system. -->

## Key concept
Timeouts and robustness in async systems.

## Task 4 — Collect Simple Metrics 📊
**Goal:** Measure how the pipeline behaves.

What to do
Track how many orders each stage processes average end-to-end latency. Print a short summary when the customer exits.

Hints: Use a shared dictionary or counters.

Each order already contains a start timestamp.

### Key concept
Basic observability in concurrent programs.

## Optional Stretch Task ⭐ — Graceful Shutdown
**Goal:** Terminate the pipeline cleanly.

### What to do
Make every stage exit when it receives None.

Do not cancel tasks manually.

Observe
Shutdown propagates naturally through the pipeline.

All tasks exit cleanly.

### Key concept
Structured concurrency and clean termination.

Notes
Do not optimize the work itself.

Do not add external libraries.

Focus on orchestration, not performance.

This exercise sets the foundation for later parts of the workshop, where the
same pipeline will be reused with faster CPU and GPU backends.