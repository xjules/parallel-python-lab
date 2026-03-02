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


async def main_duration():
    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)
        return f"Sleeping for {sleep_time} seconds"

    sleep2 = asyncio.create_task(my_job(2))
    sleep3 = asyncio.create_task(my_job(3))
    result1 = await my_job(2)
    result2 = await sleep2
    result3 = await sleep3
    print(result1)
    print(result2)
    print(result3)


async def main_wait_for():
    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)
        return f"Sleeping for {sleep_time} seconds"

    sleep2 = asyncio.create_task(my_job(200))
    try:
        await asyncio.wait_for(sleep2, timeout=1)
    except asyncio.exceptions.TimeoutError:
        print(f"Task {sleep2.cancelled()=}")


async def main_wait_for_with_shield():
    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)
        print(f"Finished sleeping for {sleep_time} seconds")

    sleep2 = asyncio.create_task(my_job(10))
    try:
        await asyncio.wait_for(asyncio.shield(sleep2), timeout=1)
    except asyncio.exceptions.TimeoutError:
        print(f"Task {sleep2.cancelled()=}")
    await sleep2


async def main_future():
    async def my_job(sleep_time, future):
        await asyncio.sleep(sleep_time)
        future.set_result(sleep_time)
        await asyncio.sleep(1.0)

    future = asyncio.Future()
    sleep_task = asyncio.create_task(my_job(3, future))
    print(f"Future done: {future.done()}")
    value = await future
    print(f"Future done: {future.done()}")
    print(f"Future value: {value}")
    await sleep_task


async def main_cancel():
    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)
        return f"Sleeping for {sleep_time} seconds"

    sleep2 = asyncio.create_task(my_job(200))
    await asyncio.sleep(1)
    if not sleep2.done():
        sleep2.cancel()
    await sleep2
    # try:
    #     await sleep2
    # except asyncio.CancelledError:
    #     print("Task was cancelled")


if __name__ == "__main__":

    start = time.time()
    # asyncio.run(main_duration())
    # asyncio.run(main_cancel())
    # asyncio.run(main_wait_for())
    # asyncio.run(main_wait_for_with_shield())
    # asyncio.run(main_future())
    asyncio.run(main_CPU_bound())
    end = time.time()
    print(f"Execution time: {end - start:.2f} seconds")
