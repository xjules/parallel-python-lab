---
marp: true
theme: dracula
class: invert
paginate: true
size: 16:9
---
# Tasks
- Submits a coroutine to the event loop in the background
  - Scheduled immediately
  - Runs concurrently
``` python
cook = Cook()
consumer = Consumer():
task1 = asyncio.create_task(cook.run())
task2 = asyncio.create_task(consumer.run())
```

---
# Await tasks
- direct handle on a task
```python
tasks = [asyncio.create_task(Cook(i).run()) for i in range(10)]
```
- raise exception by gather
```python
results = await asyncio.gather(*tasks, return_exceptions=False)
```
- return exception by gather
```python
results = await asyncio.gather(*tasks, return_exceptions=True)
```
---

# Futures - tasks

- Placeholder for a result
  - promise of a value
- Lower-level primitives
- Tasks are built on Futures
```python
tasks = [asyncio.create_task(Cook(i).run()) for i in range(10)]
```

---
# Futures - event

``` python
class Cook:
    async def do_sth_else(fut):
        # do sth else
        fut.set_result("sth else done")

    async def run(self):
        my_loop = asyncio.get_running_loop()
        fut_event = my_loop.create_future()
        asyncio.create_task(self.do_sth(fut_event))
        await fut_event
```
---

# Async context manager

- asynchronous version of the with statement 
- It uses async with to handle resources
- await to open or close 
- `__aenter__` and `__aexit__` 
- Non-blocking cleanup

### Note: implement async with foodtruck:

---

# Async context manager - alternative

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def seismic_file_access():
    print("Opening file...")
    try:
        yield "seismic file"
    finally:
        print("Closing file...")
```

---

# Async Iterators

``` python
async def async_range(count):
    for i in range(count):
        await asyncio.sleep(0.5)
        yield i

async for number in async_range(5):
    print(f"N: {number}")
```