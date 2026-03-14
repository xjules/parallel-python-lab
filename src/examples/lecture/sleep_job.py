import asyncio
import time


async def main_duration():
    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)
        return f"Sleeping for {sleep_time} seconds"

    sleep2 = asyncio.create_task(my_job(2))
    sleep3 = asyncio.create_task(my_job(3))
    result2 = await sleep2
    result3 = await sleep3
    print(result2)
    print(result3)


async def main_duration_extended():
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


async def main_cancel_1():
    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)
        return f"Sleeping for {sleep_time} seconds"

    sleep2 = asyncio.create_task(my_job(200))
    await asyncio.sleep(1)
    if not sleep2.done():
        sleep2.cancel()
    try:
        await sleep2
    except asyncio.CancelledError:
        print("Task was cancelled")


async def main_cancel_2():
    async def my_job(sleep_time):
        try:
            await asyncio.sleep(sleep_time)
        except asyncio.CancelledError:
            return "Task was cancelled!"
        return f"Sleeping for {sleep_time} seconds"

    sleep2 = asyncio.create_task(my_job(200))
    await asyncio.sleep(1)
    if not sleep2.done():
        sleep2.cancel()
    result = await sleep2
    print(result)


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


async def main_gather():
    future = asyncio.Future()

    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)

        future.set_result(sleep_time)
        return f"Sleeping for {sleep_time} seconds"

    sleep2 = asyncio.create_task(my_job(2))
    results = await asyncio.gather(sleep2, future)
    print(results)


async def main_gather_invalide_state():
    future = asyncio.Future()

    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)

        future.set_result(sleep_time)
        return f"Sleeping for {sleep_time} seconds"

    sleep2 = asyncio.create_task(my_job(2))
    results = await asyncio.gather(my_job(3), sleep2, future, return_exceptions=True)
    print(results)


async def main_context_manager():
    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)
        return f"Sleeping for {sleep_time} seconds"

    with asyncio.TaskGroup() as tg:
        future = tg.Future()
        sleep1 = tg.create_task(my_job(1))
        sleep2 = tg.create_task(my_job(2))
        sleep3 = tg.create_task(my_job(3))
        future.set_result("Future is done!")
    print(sleep1.result())
    print(sleep2.result())
    print(sleep3.result())


if __name__ == "__main__":

    start = time.time()
    # asyncio.run(main_duration())
    # asyncio.run(main_cancel_1())
    # asyncio.run(main_cancel_2())
    # asyncio.run(main_wait_for())
    # asyncio.run(main_wait_for_with_shield())
    # asyncio.run(main_future())
    # asyncio.run(main_gather())
    asyncio.run(main_context_manager())

    end = time.time()
    print(f"Execution time: {end - start:.2f} seconds")
