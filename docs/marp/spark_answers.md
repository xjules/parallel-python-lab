# Answer key — From Concurrency to Full Parallelism in Modern Python

Companion to [spark_sep_2026.md](spark_sep_2026.md). Answers follow the same order as the audience prompts.

## Concurrency or parallelism?

**Correct: B.** Concurrency means tasks make overlapping progress; parallelism means operations execute at the same time. Concurrency does not require multiple cores.

## Understanding the bottlenecks

**Correct: A — 10,000 HTTP requests.** The requests spend much of their time waiting, so concurrency can overlap those waits. Image processing is typically CPU-bound and benefits from parallel execution, not asyncio by itself.

## GIL in standard CPython

**Correct: B — no, usually not for pure-Python CPU work.** In a standard GIL-enabled CPython interpreter, only one thread at a time executes Python bytecode in that interpreter.

**Code fix needed for the demo:** initialize `total` before incrementing it, or the function raises `UnboundLocalError`:

```python
def work():
    total = 0
    for _ in range(10**8):
        total += 1
```

## Asyncio: what is printed?

**Correct: B — `finished`, followed by a possible unawaited-coroutine warning.** Calling `greet()` creates a coroutine object; it does not execute its body. The coroutine must be awaited or scheduled as a task.

## The sleep job

**Correct: B — about 3 seconds.** Both tasks are scheduled before awaiting the first. Their sleeps overlap, so the total is close to the longer sleep, not the sum.

## Mixed awaits — I

**Correct: B — about 3 seconds.** The two tasks have been scheduled before the direct two-second coroutine is awaited. They progress while that direct coroutine sleeps; after it finishes, the two-second task is already done and the three-second task has about one second left.

## Mixed awaits — II

**Correct: C — about 5 seconds.** The scheduled tasks take about three seconds in total; the final direct two-second sleep starts after those tasks have completed.

## `gather` result order

**Correct: A — `['A', 'B']`.** `asyncio.gather()` returns results in the order of its input awaitables, even though B completes before A.

## CPU work inside asyncio — version I

**Correct: C — about 6 seconds**, assuming each CPU job takes about two seconds and the program awaits task completion. Tasks are queued in this order: CPU job A, CPU job B, then the sleep. The CPU coroutines do not yield, so each blocks the event loop; the two-second sleep starts only after both CPU jobs finish.

## CPU work inside asyncio — version II

**Correct: B — about 4 seconds**, assuming the program awaits task completion. The sleep task is queued first, but after it yields, the two CPU coroutines each block the event loop for about two seconds. The sleep timer expires while the loop is blocked and is handled once the CPU jobs finish.

**Important:** As shown on the slide, this snippet creates tasks but does not await them or otherwise keep the program alive to measure their duration. Add awaits (for example, `await asyncio.gather(task_sleep, task_a, task_b)`) before presenting a duration question.

## Is this file access async?

**Correct: B.** `async def` and `asyncio.gather()` do not make synchronous `open()` or `file.read()` non-blocking. Those calls still run on and block the event-loop thread.

## What does `to_thread` solve?

**Correct: B.** `asyncio.to_thread()` runs a blocking synchronous function in a worker thread, keeping that work from freezing the event loop. It does not automatically make pure-Python CPU work parallel on a standard GIL-enabled build.

## One hundred workers

**Correct: B.** Bound concurrency to avoid overwhelming CPU, memory, or downstream services. A semaphore, queue, or fixed-size worker pool can limit how many operations are active at once.

## Free-threaded Python: what changed?

**Correct: B.** Free-threaded CPython is officially supported as an optional build starting with Python 3.14. It is not the default installation, and Python 3.13's free-threaded build was experimental.

## Is the GIL actually off?

**Key point:** `sys._is_gil_enabled()` reports the runtime GIL state. A free-threaded-capable build may run with the GIL enabled, including if an imported extension is not marked as supporting free-threading. Check after importing dependencies.

## Interpreter workers: isolation is the tradeoff

**Correct: B.** `InterpreterPoolExecutor` runs each worker in its own interpreter, with its own GIL. Mutable Python objects are not shared directly; inputs and results are serialized between interpreters.

## How does a thread report back?

**Correct: A.** `asyncio.Queue` is not thread-safe. A worker thread should schedule queue operations on the event-loop thread with `loop.call_soon_threadsafe(...)`.

## Choose the model

- **A — 10,000 slow HTTP requests:** `asyncio` is a good fit because the workload is dominated by I/O waits.
- **B — pure-Python numerical work on a free-threaded build:** use free-threaded threads for parallel execution. A process pool or Python 3.14 `InterpreterPoolExecutor` is another option, with different isolation and serialization tradeoffs.
- **C — downloads followed by heavy calculations:** combine async I/O orchestration with a bounded worker pool for the CPU work.
