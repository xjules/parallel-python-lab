import asyncio
import time


def heavy_calculation(n):
    return sum(i * i for i in range(n))


async def main():
    start = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        for _ in range(20):
            tg.create_task(asyncio.to_thread(heavy_calculation, 10**7))

    print(f"Total time: {time.perf_counter() - start:.2f}s")


asyncio.run(main())
