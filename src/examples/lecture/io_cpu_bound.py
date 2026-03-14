import asyncio
import time
from signal import SIGINT

import aiofiles


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


async def main_disk_read():
    async def read_file(path):
        with open(path, "rb") as f:
            return f.read()

    t1 = asyncio.create_task(read_file("file1.txt"))
    t2 = asyncio.create_task(read_file("file2.txt"))

    await asyncio.gather(t1, t2)


async def main_disk_read_to_thread():
    def read_file(path):
        with open(path, "rb") as f:
            return f.read()

    async def read_task(path):
        print(f"reading file {path} ")
        content = await asyncio.to_thread(read_file, path)
        print(f"read {len(content)} characters from {path}")

    t1 = asyncio.create_task(read_task("file1.txt"))
    t2 = asyncio.create_task(read_task("file2.txt"))

    await asyncio.gather(t1, t2)


async def main_disk_read_run_in_executor():
    def read_file(path):
        with open(path, "rb") as f:
            return f.read()

    async def read_task(path):
        print(f"reading file {path} ")
        loop = asyncio.get_running_loop()
        content = await loop.run_in_executor(None, read_file, path)
        print(f"read {len(content)} characters from {path}")

    t1 = asyncio.create_task(read_task("file1.txt"))
    t2 = asyncio.create_task(read_task("file2.txt"))

    await asyncio.gather(t1, t2)


async def main_disk_read_with_aiofiles():
    async def read_file(path):
        async with aiofiles.open(path, "rb") as f:
            return await f.read()

    async def read_task(path):
        print(f"reading file {path} ")
        content = await read_file(path)
        print(f"read {len(content)} characters from {path}")

    t1 = asyncio.create_task(read_task("file1.txt"))
    t2 = asyncio.create_task(read_task("file2.txt"))

    await asyncio.gather(t1, t2)


async def main_loop_signal_handler():
    def cancel_tasks():
        tasks = asyncio.all_tasks()
        for task in tasks:
            task.cancel()
        print("Cancelled all tasks")

    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)
        return f"Sleeping for {sleep_time} seconds"

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(SIGINT, cancel_tasks)
    await my_job(30)


def run_func_async(func):
    print(f"Running {func.__name__}...")
    start = time.time()
    asyncio.run(func())
    end = time.time()
    print(f"Execution time: {end - start:.2f} seconds")


if __name__ == "__main__":
    # run_func_async(main_CPU_bound)
    # run_func_async(main_disk_read)
    # run_func_async(main_disk_read_to_thread)
    # run_func_async(main_disk_read_run_in_executor)
    # run_func_async(main_disk_read_with_aiofiles)
    run_func_async(main_loop_signal_handler)
