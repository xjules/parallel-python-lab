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


async def main_disk_read():
    def read_file(path):
        with open(path, "r") as f:
            return f.read()

    async def read_task(name, path):
        print(f"{name} reading file")
        content = await asyncio.to_thread(read_file, path)
        print(f"{name} read {len(content)} characters")

    t1 = asyncio.create_task(read_task("A", "file1.txt"))
    t2 = asyncio.create_task(read_task("B", "file2.txt"))

    await asyncio.gather(t1, t2)


if __name__ == "__main__":

    start = time.time()
    # asyncio.run(main_CPU_bound())
    asyncio.run(main_disk_read())

    end = time.time()
    print(f"Execution time: {end - start:.2f} seconds")
