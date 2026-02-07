
# Simulation Factory

You process many independent jobs:

- Load input data (I/O)
- Run a numerical kernel
- Aggregate and store results

Jobs vary in runtime → perfect for concurrency and parallelism.

## Agenda (Full Day, progressive complexity)

### 1. Concurrent design first (Async as control layer)

- Concurrency vs parallelism
- Async pipelines and task orchestration
- Structured concurrency (TaskGroup)
- Cancellation, backpressure, bounded concurrency

**Outcome:** async pipeline coordinating many jobs, CPU kernel still naive

### 2. CPU parallelism with Numba

- Identifying compute hotspots
- Numba compilation model
- njit, prange, parallel=True, nogil
- Integrating CPU kernels into async pipelines (to_thread)

**Outcome:** same pipeline, CPU kernel now parallel and fast

### 3. GPU execution with OpenCL (via Python)

- GPU execution model refresher
- OpenCL kernels and queues
- Host–device transfers
- Blocking vs non-blocking GPU calls
- Calling OpenCL kernels from async pipelines

**Outcome:** switchable CPU / GPU backend inside the same pipeline

### 4. Throughput, overlap, and scaling

- CPU–GPU overlap
- Batching strategies
- Queue-based producer/consumer patterns
- Keeping devices busy
- Failure handling across async + compute layers

**Outcome:** high-throughput, scalable concurrent system

### 5. Wrap-up: from design to full parallelism

- What async gives you (control, correctness)
- What Numba gives you (CPU parallelism)
- What OpenCL gives you (massive parallelism)
- When to use each

## Key narrative thread

Async orchestrates work → Numba accelerates CPU kernels → OpenCL unlocks massive parallelism.

One example. One pipeline. More power at each step.

## Next steps

I can:
- Reduce this to a half-day version
- Write a one-page exercise handout
- Sketch the starter code structure (step-by-step branches)

