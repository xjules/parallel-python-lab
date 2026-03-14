import asyncio
import time


async def main_CPU_bound_message_send():

    event_queue = asyncio.Queue()
    loop = asyncio.get_running_loop()

    async def send_message(message):
        await event_queue.put(message)

    def cpu_bound_job(job_id, n):
        asyncio.run_coroutine_threadsafe(
            send_message(f"starting job {job_id}..."), loop
        )
        count = 0
        for i in range(n):
            count += i
            if n // 2 == i:
                asyncio.run_coroutine_threadsafe(
                    send_message(f"halfway through job {job_id}..."), loop
                )
        asyncio.run_coroutine_threadsafe(send_message(f"finished job {job_id}"), loop)
        return count

    async with asyncio.TaskGroup() as tg:
        for i in range(20):
            tg.create_task(asyncio.to_thread(cpu_bound_job, i, 10**9))

        while True:
            message = await event_queue.get()
            print(message)
            event_queue.task_done()


async def main_CPU_bound_message_queue():
    event_queue = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def cpu_bound_job(job_id, n):
        loop.call_soon_threadsafe(event_queue.put_nowait, f"starting job {job_id}...")
        count = 0
        for i in range(n):
            count += i
            if n // 2 == i:
                loop.call_soon_threadsafe(
                    event_queue.put_nowait, f"halfway through job {job_id}..."
                )
        loop.call_soon_threadsafe(event_queue.put_nowait, f"finished job {job_id}")
        return count

    async with asyncio.TaskGroup() as tg:
        for i in range(20):
            tg.create_task(asyncio.to_thread(cpu_bound_job, i, 10**9))

        while True:
            message = await event_queue.get()
            print(message)
            event_queue.task_done()


async def main_CPU_bound():
    def cpu_bound_job(job_id, n):
        print(f"Starting job {job_id}...")
        count = 0
        for i in range(n):
            count += i
        print(f"Finished job {job_id}")
        return count

    async with asyncio.TaskGroup() as tg:
        for i in range(20):
            tg.create_task(asyncio.to_thread(cpu_bound_job, i, 10**9))


def run_func_async(func):
    print(f"Running {func.__name__}...")
    start = time.time()
    asyncio.run(func())
    end = time.time()
    print(f"Execution time: {end - start:.2f} seconds")


if __name__ == "__main__":
    # run_func_async(main_CPU_bound)
    # run_func_async(main_CPU_bound_message_queue)
    run_func_async(main_CPU_bound_message_send)
