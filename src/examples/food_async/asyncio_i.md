---
marp: true
theme: dracula
class: invert
paginate: true
size: 16:9
---
# Coroutines

``` python
async def run():
    await something()
    ...
    await something_else()
```

- `async def` creates a coroutine
- `await` yields control to the event loop
    - requires **an event loop!**
- Normal functions block
- Coroutines can cooperate
- Calling a coroutine function **does not run the code**.

---
# The `await`
- The Suspension Point - used to pause the current coroutine until the awaited operation finishes
- **Yielding Control** - when you `await`, you tell the Event Loop: 
    - _"I am waiting; go ahead and run something else in the meantime"_
- `await` can **only** be used inside a coroutine, `async def`

---
# `asyncio.gather`
- runs and await multiple coroutines
- Results are in the same same order as the inputs
- It automatically turns coroutines into tasks
``` python
class Cook:
    async def run():
        await cook()
class Consumer:
    async def run():
        await eat()
results = await asyncio.gather(Cook().run(), Consumer.run()):
```


---
# Event loop - central scheduler
- The core of every `asyncio` application that manages and distributes execution
- Execution Model runs in a **single thread** and performs three primary jobs
    - **Monitor** OS I/O events (network sockets, pipes, etc.).
    - **Run** ready callbacks and scheduled tasks
    - **Resume** coroutines whose awaited operations (like I/O) have completed
---

# Event loop - managing concurrency
- The Loop Cycle - maintains a queue of tasks and runs them one at a time until a task hits `await`
- Yielding control - when a coroutine hits `await`, it pauses and tells the loop: 
    - _I am waiting for I/O; run something else in the meantime_

---
# Event loop - efficiency

- OS Notification
    - The loop uses efficient system-level APIs (**epoll**, **kqueue**, or **IOCP**) to track these pauses without wasting CPU cycles
    - Thousands of "ultra-light" tasks can overlap on a single CPU core, creating massive concurrency for I/O-bound workloads


---
# Event loop - creation `asyncio.run()`
- The recommended way to launch an async application
- Automated Lifecycle that performs three critical steps:
    1. Creates a brand-new **Event Loop**
    2. Runs the main coroutine until completion
    3. Handles cleanup and closes the loop automatically

``` python
class Cook:
    async def run():
        my_loop = asyncio.get_running_loop()
        await make_fries()
asyncio.run(Cook.run())
```
---

# Event Loop - run sync tasks concurrently

``` python
class Cook:
    def sync_io_task_1():
        # heavy job
    def sync_io_task_2():
        # heavy job
    async def run():
        my_loop = asyncio.get_running_loop()
        tasks = [
            loop.run_in_executor(None, sync_io_task_1),
            loop.run_in_executor(None, sync_io_task_2),
        ]
        results = await asyncio.gather(*tasks)

cook = Cook()
asyncio.run(cook.run())
```