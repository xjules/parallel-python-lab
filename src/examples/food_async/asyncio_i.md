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
    # python code
    await something_else()
```

-   `async def` creates a coroutine
-   `await` yields control to the event loop
-   Normal functions block
-   Coroutines can cooperate

---
# Gather

``` python
class Cook:
    async def run():
        await cook()
class Consumer:
    async def run():
        await eat()
cook = Cook()
consumer = Consumer()
results = await asyncio.gather(cook.run(), consumer.run()):
```
- `asyncio.gather` runs and await multiple coroutines
- results are in the same same order as the inputs

---

# The Event Loop - basic

- central scheduler
- runs tasks
- monitors I/O readiness
- switches between coroutines


---

# The Event Loop - creation

- creates, runs cook on and closes the loop afterwards
``` python
class Cook:
    async def run():
        my_loop = asyncio.get_running_loop()
        await make_fries()

cook = Cook()
asyncio.run(cook.run())
```

---

# The Event Loop - run sync tasks concurrently

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