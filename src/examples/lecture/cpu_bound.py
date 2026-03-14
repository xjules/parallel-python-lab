import asyncio
import time


async def main_CPU_bound():
    async def cpu_bound_job(n):
        count = 0
        for i in range(n):
            count += i
        return count

    task_sum_1 = asyncio.create_task(cpu_bound_job(10**8))
    task_sum_2 = asyncio.create_task(cpu_bound_job(10**8))
    task_sleep = asyncio.create_task(asyncio.sleep(2))  # 2secs
    result1 = await task_sum_1
    result2 = await task_sum_2
    await task_sleep
    print(f"Result 1: {result1}")
    print(f"Result 2: {result2}")


if __name__ == "__main__":

    start = time.time()
    # asyncio.run(main_duration())
    # asyncio.run(main_cancel_1())
    # asyncio.run(main_cancel_2())
    # asyncio.run(main_wait_for())
    # asyncio.run(main_wait_for_with_shield())
    # asyncio.run(main_future())
    # asyncio.run(main_gather())
    # asyncio.run(main_CPU_bound())

    end = time.time()
    print(f"Execution time: {end - start:.2f} seconds")
