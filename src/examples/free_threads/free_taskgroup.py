import asyncio
import time


def heavy_calculation(n):
    # This now runs in parallel on multiple cores in 3.13t
    return sum(i * i for i in range(n))


async def main():
    start = time.perf_counter()
    # Run 4 heavy tasks in parallel threads
    async with asyncio.TaskGroup() as tg:
        for _ in range(20):
            tg.create_task(asyncio.to_thread(heavy_calculation, 10**10))

    print(f"Total time: {time.perf_counter() - start:.2f}s")


asyncio.run(main())
