---
marp: true
theme: dracula
class: invert
paginate: true
size: 16:9
---
# Asyncio

standard python library to write concurrent code

- Single-threaded
- Cooperative multitasking
- Tasks explicitly yield control

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
The Suspension Point - used to pause the current coroutine until the awaited operation finishes

- **Yielding Control** - when you `await`, you tell the Event Loop: 
    - _"I am waiting; go ahead and run something else in the meantime"_
- `await` can **only** be used inside a coroutine, `async def`

---
# Tasks
Represents the actual **concurrency**

- Submits a coroutine to the event loop in the [background](../../src/examples/sleep_job/my_job.py)
  - Scheduled and starts immediately
  - Runs concurrently
``` python
async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)

sleep2 = asyncio.create_task(my_job(2))
sleep3 = asyncio.create_task(my_job(3))
await sleep2
await sleep3
```
---
# Tasks - results
- awaiting tasks delivers results!
``` python
async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)
    return f"Sleeping for {sleep_time} seconds"

sleep2 = asyncio.create_task(my_job(2))
sleep3 = asyncio.create_task(my_job(3))
result2 = await sleep2
result3 = await sleep3
```
---
# Tasks - mix
- how long this takes?
``` python
async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)

sleep2 = asyncio.create_task(my_job(2))
sleep3 = asyncio.create_task(my_job(3))
await my_job(2)
await sleep2
await sleep3
```
[Execution](./execution_ex.md)

---
# Tasks - cancellation
very straightforward!
```python
async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)

sleep_job = asyncio.create_task(my_job(100))
await asyncio.sleep(1)
sleep_job.cancel()
#...
await sleep_job

```
---
# Tasks - cancellation
propagated and not handled
```python
sleep_job.cancel()
#...
await sleep_job

```
```
asyncio/tasks.py", line 718, in sleep_job
    return await future
           ^^^^^^^^^^^^
asyncio.exceptions.CancelledError
```
---
# Tasks - cancellation
handling - I.
```python
async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)

sleep_job = asyncio.create_task(my_job(100))
await asyncio.sleep(1)
sleep_job.cancel()
#...
try:
    await sleep_job
except asyncio.CancellationError
  ...
```
---
# Tasks - cancellation
handling - II.
```python
async def my_job(sleep_time):
    try:
        await asyncio.sleep(sleep_time)
    except asyncio.CancellationError
        pass

sleep_job = asyncio.create_task(my_job(100))
await asyncio.sleep(1)
sleep_job.cancel()
await sleep_job
```

---
# Task - timeout cancellation
```python
async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)

sleep_task = asyncio.create_task(my_job(100))
try:
    await asyncio.wait_for(sleep_task, timeout=1)
except asyncio.exceptions.TimeoutError:
    print(f"Task {sleep_task.cancelled()=}")
```
---
# Task - shield
```python
async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)

sleep_task = asyncio.create_task(my_job(10))
try:
    await asyncio.wait_for(asyncio.shield(sleep_task), timeout=1)
except asyncio.exceptions.TimeoutError:
    print(f"Task {sleep_task.cancelled()=}")
await sleep_task
```
---
# Awaitables

```
          Awaitable  (anything you can "await")
           ┌──────────────┴──────────────┐
       Coroutine                      Future
    (async def fn)            (placeholder for a result;
     yields control            set_result / set_exception)
                                     │
                                   Task
                            (Future + scheduled Coroutine;
                             created via create_task())
```
- **Future** — low-level: _pending → result/exception_
- **Task** — a `Future` that wraps & drives a coroutine on the event loop
---
# `asyncio.gather`
runs and await multiple awaitables
- Results are in the same same order as the inputs
- It automatically turns coroutines into tasks
``` python
async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)
    return f"Sleeping for {sleep_time} seconds"

future = asyncio.Future()
sleep2 = asyncio.create_task(my_job(2))
results = await asyncio.gather(my_job(3), sleep2, future)
print(results)
```

---
# Future
Placeholder for a result
- promise of a value
- lower-level primitives
```python
async def my_job(sleep_time, future):
    await asyncio.sleep(sleep_time)
    future.set_result(sleep_time)
    await asyncio.sleep(1.0)

future = asyncio.Future()
sleep_task = asyncio.create_task(my_job(10, future))
value = await future # assert value==10
await sleep_task
```
---
# Future - note!
Cannot be set twice or more!

```python
future = asyncio.Future()

async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)
    
    future.set_result(sleep_time)
    return f"Sleeping for {sleep_time} seconds"

sleep2 = asyncio.create_task(my_job(2))
results = await asyncio.gather(my_job(3), sleep2, future)
```
---
# Gather - note!
Cannot be set twice or more!

```python
future = asyncio.Future()

async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)
    
    future.set_result(sleep_time)
    return f"Sleeping for {sleep_time} seconds"

sleep2 = asyncio.create_task(my_job(2))
# let's not raise!
results = await asyncio.gather(my_job(3), sleep2, future, return_exceptions=True)
```

---
# Future - note!
Cannot be set twice or more!

```python
future = asyncio.Future()

async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)
    if not future.done(): #  make sure it is not done already
        future.set_result(sleep_time)
    return f"Sleeping for {sleep_time} seconds"

sleep2 = asyncio.create_task(my_job(2))
results = await asyncio.gather(my_job(3), sleep2, future)
```
---
# CPU bound code
code might execute sequentially

```python
async def cpu_bound_job(n):
    count = 0
    for i in range(n):
        count += i
    return count

    task_sum_1 = asyncio.create_task(cpu_bound_job(10**8)) #2secs
    task_sum_2 = asyncio.create_task(cpu_bound_job(10**8)) #2secs
    result1 = await task_sum_1
    result2 = await task_sum_2
    print(f"Results: {result1=} {result2=}")
```
---
# CPU bound code
- parallelization might help
```python
async def cpu_bound_job(n):
    count = 0
    for i in range(n):
        count += i
    return count

    task_sum_1 = asyncio.create_task(cpu_bound_job(10**8)) #2secs
    task_sum_2 = asyncio.create_task(cpu_bound_job(10**8)) #2secs
    task_sleep = asyncio.create_task(asyncio.sleep(2)) #2secs
    result1 = await task_sum_1
    result2 = await task_sum_2
    await task_sleep
    print(f"Results: {result1=} {result2=}")
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
async def main_task():
    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)

    sleep2 = asyncio.create_task(my_job(2))
asyncio.run(main_task(), debug=True)
```
---
# Event loop - direct access
``` python
async def main_task():
    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)

    loop = asyncio.get_running_loop()
    loop.call_soon(my_job)
asyncio.run(main_task())
```
---
# Event loop - signal handlers
``` python
async def main_task():
    def cancel_tasks():
        tasks = asyncio.all_tasks()
        [task.cancel() for task in tasks]
    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, cancel_tasks)
asyncio.run(main_task())
```
---

# Event Loop - run sync tasks concurrently

``` python

def sync_job_1():
    # heavy job
def sync_job_2():
    # heavy job
async def run():
    my_loop = asyncio.get_running_loop()
    tasks = [
        loop.run_in_executor(None, sync_io_task_1),
        loop.run_in_executor(None, sync_io_task_2),
    ]
    results = await asyncio.gather(*tasks)
asyncio.run(run())
```