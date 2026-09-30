"""Runnable standard-library demos for docs/marp/spark_sep_2026.md.

Choose demos in the ``__main__`` block by uncommenting the desired call(s),
similar to io_cpu_bound.py. Adjust the constants below to change run sizes.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import inspect
import sys
import tempfile
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

# Match the CPU timing examples in the slides: on a fast laptop, 10**8
# iterations takes roughly two seconds. Reduce these values for a quick run.
# FILE_SIZE_MB controls the temporary files created by the I/O demos.
ITERATIONS = 10**8
DELAY = 2.0
JOBS = 4
WORKERS = 2
FILE_SIZE_MB = 4


def cpu_work(iterations: int) -> int:
    """A small, pure-Python CPU workload shared by thread/interpreter demos."""
    total = 0
    for value in range(iterations):
        total += value
    return total


async def sleep_demo(delay: float) -> None:
    """Schedule two sleepers together; elapsed time is about the longer delay."""

    async def job(seconds: float) -> str:
        await asyncio.sleep(seconds)
        return f"Slept for {seconds:g} seconds"

    start = time.perf_counter()
    task_a = asyncio.create_task(job(delay))
    task_b = asyncio.create_task(job(delay * 1.5))
    print(await task_a)
    print(await task_b)
    print(f"Elapsed: {time.perf_counter() - start:.2f}s (overlapping waits)")


def blocking_demo(delay: float) -> None:
    """Compare sequential blocking waits with overlapping async waits."""
    start = time.perf_counter()
    time.sleep(delay)
    time.sleep(delay * 1.5)
    print(f"Sequential blocking waits: {time.perf_counter() - start:.2f}s")
    asyncio.run(sleep_demo(delay))


async def coroutine_demo() -> None:
    """Show that calling async def makes a coroutine; scheduling runs it."""

    async def greet() -> None:
        print("hello")

    pending = greet()
    print("Called greet(); its body has not run yet.")
    pending.close()  # Avoid an unawaited-coroutine warning in this teaching demo.
    await greet()
    task = asyncio.create_task(greet())
    await task


async def mixed_await_demo(delay: float, direct_first: bool) -> None:
    """Demonstrate how already-scheduled tasks progress during a direct await."""

    async def job(seconds: float) -> str:
        await asyncio.sleep(seconds)
        return f"Slept for {seconds:g} seconds"

    start = time.perf_counter()
    task_a = asyncio.create_task(job(delay))
    task_b = asyncio.create_task(job(delay * 1.5))
    if direct_first:
        await job(delay)
        await task_a
        await task_b
        expected = "about the longer scheduled sleep"
    else:
        await task_a
        await task_b
        await job(delay)
        expected = "scheduled sleeps plus the final direct sleep"
    print(f"Elapsed: {time.perf_counter() - start:.2f}s ({expected})")


async def gather_order_demo(delay: float) -> None:
    """Completion order differs from asyncio.gather's input/result order."""
    start = time.perf_counter()
    results = await asyncio.gather(
        asyncio.sleep(delay * 1.5, result="A"),
        asyncio.sleep(delay, result="B"),
    )
    print(f"B finishes before A; gather results: {results}")
    print(f"Elapsed: {time.perf_counter() - start:.2f}s")


async def cpu_async_demo(iterations: int, delay: float, sleep_first: bool) -> None:
    """CPU coroutines do not yield, so they block the event loop and its timer."""

    async def cpu_job(label: str) -> int:
        print(f"Starting CPU job {label}")
        result = cpu_work(iterations)
        print(f"Finished CPU job {label}")
        return result

    start = time.perf_counter()
    if sleep_first:
        sleep_task = asyncio.create_task(asyncio.sleep(delay), name="sleep")
        task_a = asyncio.create_task(cpu_job("A"))
        task_b = asyncio.create_task(cpu_job("B"))
    else:
        # The slide's version I queues CPU jobs before the sleep task.
        task_a = asyncio.create_task(cpu_job("A"))
        task_b = asyncio.create_task(cpu_job("B"))
        sleep_task = asyncio.create_task(asyncio.sleep(delay), name="sleep")

    await asyncio.gather(task_a, task_b, sleep_task)
    print(f"Elapsed: {time.perf_counter() - start:.2f}s")
    print("Expected: CPU jobs run consecutively; the sleep cannot interrupt them.")


def write_demo_file(path: Path, size_mb: int) -> None:
    block = b"spark demo data\n" * (1024 * 1024 // len(b"spark demo data\n"))
    with path.open("wb") as output:
        for _ in range(size_mb):
            output.write(block)


async def file_io_demo(method: str, size_mb: int) -> None:
    """Contrast synchronous reads on the loop with reads moved to worker threads."""
    with tempfile.TemporaryDirectory(prefix="spark-demo-") as directory:
        paths = [Path(directory) / f"file{index}" for index in (1, 2)]
        for path in paths:
            write_demo_file(path, size_mb)

        async def read(path: Path) -> int:
            if method == "thread":
                content = await asyncio.to_thread(path.read_bytes)
            else:
                # This intentionally blocks the event-loop thread, despite async def.
                content = path.read_bytes()
            print(f"Read {len(content):,} bytes from {path.name}")
            return len(content)

        start = time.perf_counter()
        await asyncio.gather(*(read(path) for path in paths))
        print(f"Elapsed: {time.perf_counter() - start:.2f}s ({method} file reads)")


async def to_thread_sum_demo() -> None:
    """Compare two pure-Python sums in sequence and with asyncio.to_thread()."""
    iterations = 10**8
    gil_check = getattr(sys, "_is_gil_enabled", None)
    gil_enabled = gil_check() if gil_check is not None else "unknown"
    print(f"Python: {sys.version.split()[0]}; GIL enabled: {gil_enabled}")
    print(f"Summing range({iterations:,}) twice")

    start = time.perf_counter()
    sequential_results = [cpu_work(iterations), cpu_work(iterations)]
    sequential_elapsed = time.perf_counter() - start

    start = time.perf_counter()
    threaded_results = await asyncio.gather(
        asyncio.to_thread(cpu_work, iterations),
        asyncio.to_thread(cpu_work, iterations),
    )
    threaded_elapsed = time.perf_counter() - start

    assert threaded_results == sequential_results
    print(f"Sequential: {sequential_elapsed:.2f}s")
    print(f"Two to_thread jobs: {threaded_elapsed:.2f}s")
    print(f"Observed speedup: {sequential_elapsed / threaded_elapsed:.2f}x")


async def bounded_demo(iterations: int, jobs: int, workers: int) -> None:
    """Keep active thread work bounded even when many coroutines are submitted."""
    semaphore = asyncio.Semaphore(workers)
    active = 0
    maximum_active = 0
    state_lock = threading.Lock()

    def tracked_work() -> int:
        nonlocal active, maximum_active
        with state_lock:
            active += 1
            maximum_active = max(maximum_active, active)
        try:
            return cpu_work(iterations)
        finally:
            with state_lock:
                active -= 1

    async def bounded_job() -> int:
        async with semaphore:
            return await asyncio.to_thread(tracked_work)

    start = time.perf_counter()
    results = await asyncio.gather(*(bounded_job() for _ in range(jobs)))
    print(f"Completed {len(results)} jobs; max active workers: {maximum_active}")
    print(f"Elapsed: {time.perf_counter() - start:.2f}s")


def gil_status_demo() -> None:
    is_gil_enabled = getattr(sys, "_is_gil_enabled", None)
    if is_gil_enabled is None:
        print("This Python build does not expose sys._is_gil_enabled().")
        print(f"Python: {sys.version.split()[0]}; executable: {sys.executable}")
        return
    print(f"GIL enabled: {is_gil_enabled()}")
    print("Check this after importing dependencies; an extension may enable the GIL.")


def interpreter_demo(iterations: int, workers: int) -> None:
    """Run CPU jobs in isolated interpreters when this Python provides the API."""
    interpreter_pool = getattr(concurrent.futures, "InterpreterPoolExecutor", None)
    if interpreter_pool is None:
        print("InterpreterPoolExecutor requires Python 3.14 or newer.")
        return
    with interpreter_pool(max_workers=workers) as pool:
        results = list(pool.map(cpu_work, [iterations] * workers))
    print(f"{len(results)} interpreter workers returned {results[0]:,} each.")
    print(
        "Workers have isolated interpreter state; arguments and results are serialized."
    )


async def thread_message_demo(iterations: int) -> None:
    """Send messages from a worker thread to an asyncio-owned queue safely."""
    queue: asyncio.Queue[str] = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def worker() -> int:
        loop.call_soon_threadsafe(queue.put_nowait, "worker started")
        result = cpu_work(iterations)
        loop.call_soon_threadsafe(queue.put_nowait, "worker finished")
        return result

    worker_task = asyncio.create_task(asyncio.to_thread(worker))
    for _ in range(2):
        print(f"Message received by event loop: {await queue.get()}")
        queue.task_done()
    result = await worker_task
    print(f"Worker result: {result:,}")


def run_func_async(func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
    """Run either a synchronous demo or an async demo and report its duration."""
    name = getattr(func, "__name__", str(func))
    print(f"Running {name}...")
    start = time.perf_counter()
    if inspect.iscoroutinefunction(func):
        asyncio.run(func(*args, **kwargs))
    else:
        func(*args, **kwargs)
    print(f"Execution time: {time.perf_counter() - start:.2f} seconds")


if __name__ == "__main__":
    # Uncomment the demos to run. Run one at a time for comparable timings.
    # run_func_async(blocking_demo, DELAY)
    # run_func_async(coroutine_demo)
    run_func_async(sleep_demo, DELAY)
    # run_func_async(mixed_await_demo, DELAY, direct_first=True)
    # run_func_async(mixed_await_demo, DELAY, direct_first=False)
    # run_func_async(gather_order_demo, DELAY)
    # run_func_async(cpu_async_demo, ITERATIONS, DELAY, sleep_first=False)
    # run_func_async(cpu_async_demo, ITERATIONS, DELAY, sleep_first=True)
    # run_func_async(file_io_demo, "sync", FILE_SIZE_MB)
    # run_func_async(file_io_demo, "thread", FILE_SIZE_MB)
    # run_func_async(to_thread_sum_demo)  # compare GIL and free-threaded envs
    # run_func_async(bounded_demo, ITERATIONS, JOBS * 4, WORKERS)
    # run_func_async(gil_status_demo)
    # run_func_async(interpreter_demo, ITERATIONS, WORKERS)
    # run_func_async(thread_message_demo, ITERATIONS)
