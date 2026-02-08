import asyncio
import random
import time
from dataclasses import dataclass
from typing import Dict, List

# --- Domain model ------------------------------------------------------------


@dataclass(frozen=True)
class Job:
    job_id: int
    size: int  # controls kernel cost
    io_mb: float  # controls I/O delay


# --- Pipeline stages ---------------------------------------------------------


async def load_input(job: Job) -> List[float]:
    """
    Simulate I/O-bound work: reading input from disk/network.
    Uneven latency is common in real pipelines.
    """
    # Example: "read" time scales with io_mb + jitter
    await asyncio.sleep(0.02 * job.io_mb + random.uniform(0.0, 0.05))
    # Fake "input data"
    return [random.random() for _ in range(job.size)]


def run_kernel(data: List[float]) -> float:
    """
    Naïve CPU-bound numerical kernel (intentionally NOT optimized).
    Think: likelihood eval, small PDE step, misfit, etc.
    """
    acc = 0.0
    # O(n) loop with some math; runtime varies with `len(data)`
    for x in data:
        acc += (x * x + 0.001) ** 0.5
    return acc


async def store_result(job: Job, result: float) -> None:
    """
    Simulate writing/aggregating output (I/O-bound).
    """
    await asyncio.sleep(random.uniform(0.005, 0.03))
    # In real life: write a file / push to DB / update metrics
    # Here we do nothing.


# --- Orchestration -----------------------------------------------------------


async def process_one(
    job: Job, sem: asyncio.Semaphore, stats: Dict[str, float]
) -> float:
    """
    Orchestrates one factory job end-to-end.
    """
    async with sem:  # bounded concurrency (backpressure)
        t0 = time.perf_counter()

        data = await load_input(job)  # I/O stage (async)
        result = run_kernel(data)  # CPU stage (naïve)
        await store_result(job, result)  # I/O stage (async)

        dt = time.perf_counter() - t0
        stats["completed"] += 1
        stats["total_seconds"] += dt
        return result


async def simulation_factory(
    n_jobs: int = 30,
    max_in_flight: int = 8,
) -> None:
    # Create uneven jobs: some big kernels, some tiny, varying "I/O"
    jobs = [
        Job(
            job_id=i,
            size=random.choice([20_000, 40_000, 80_000, 150_000]),
            io_mb=random.choice([0.5, 1.0, 2.0, 4.0]),
        )
        for i in range(n_jobs)
    ]

    sem = asyncio.Semaphore(max_in_flight)
    stats = {"completed": 0.0, "total_seconds": 0.0}

    t0 = time.perf_counter()
    tasks = [asyncio.create_task(process_one(job, sem, stats)) for job in jobs]

    # Aggregate results as they complete (handles uneven runtimes nicely)
    results = []
    for coro in asyncio.as_completed(tasks):
        r = await coro
        results.append(r)

    wall = time.perf_counter() - t0
    avg = stats["total_seconds"] / stats["completed"]

    print(f"Jobs: {n_jobs}, max_in_flight: {max_in_flight}")
    print(f"Wall time: {wall:.2f}s")
    print(f"Avg per-job time (sum/job): {avg:.2f}s")
    print(f"Aggregated metric (mean): {sum(results)/len(results):.4f}")


if __name__ == "__main__":
    asyncio.run(simulation_factory())
