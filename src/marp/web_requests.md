---
marp: true
theme: dracula
class: invert
paginate: true
size: 16:9

---

# Networking & Advanced Concurrency
## From Local Coroutines to Distributed Pipelines (Chapters 3 & 4)

---

### Moving to the Network: Sockets
* **Standard Sockets**: By default, sockets are **blocking**. When waiting for a client to send data, the entire thread stops [1, 2].
* **Non-blocking Sockets**: These return immediately. If no data is ready, they signal the application to "try again later" [2, 3].
* **The Async Way**: `asyncio` uses the OS event notification systems (**epoll**, **kqueue**) to watch these sockets efficiently, waking up your tasks only when data arrives [4, 5].

---

### High-Level Servers: `asyncio.start_server`
* **Beyond Sockets**: Instead of managing low-level socket objects, `asyncio` provides a high-level server API [6].
* **The Connection Callback**: You provide a coroutine that is triggered whenever a client connects [7].
* **Streams**: You interact with clients using a `StreamReader` (to read data) and a `StreamWriter` (to send data) [7, 8].
    * *Foodtruck Context*: Imagine your truck now has a "digital window" where `nc localhost 8000` sends an order directly into your pipeline [9, 10].

---

### External I/O with `aiohttp`
* **The `requests` Problem**: Standard libraries like `requests` use blocking sockets that halt the entire Event Loop [11].
* **The Solution**: `aiohttp` is an asynchronous HTTP client that uses non-blocking sockets all the way down [12, 13].
* **Context Management**: Always use `async with ClientSession()` to manage connection pooling and ensure resources are cleaned up properly [14, 15].
    * *Foodtruck Context*: Before cooking, your stage might "await" a check to an external Nutritional API via `aiohttp` [16].

---

### Managing Multiple Tasks: `asyncio.gather`
* **Parallel Execution**: While `await` runs tasks one-by-one, `gather` allows you to kick off a collection of tasks concurrently [17, 18].
* **Deterministic Results**: Even if tasks finish at different times, `gather` returns results in the **exact order** they were requested [19, 20].
* **Exception Handling**: Use `return_exceptions=True` to treat errors as successful results rather than crashing the entire batch [21, 22].

---

### Dynamic Concurrency: `as_completed`
* **Real-time Responsiveness**: `gather` makes you wait for the *slowest* task before seeing *any* results [18, 23].
* **The Iterator Pattern**: `as_completed` yields results as soon as they finish [20, 24].
    * *Foodtruck Context*: If you are cooking 5 burgers, `as_completed` lets you serve the fastest one immediately while the thicker ones continue grilling [25, 26].

---

### Decoupling with Queues
* **The Producer-Consumer Pattern**: Use `asyncio.Queue` to link your pipeline stages [27].
* **Benefits**:
    1. **Decoupling**: The "Producer" (order window) doesn't need to know how the "Consumer" (cook) works [28, 29].
    2. **Buffer Management**: A `maxsize` on the queue prevents the truck from being overwhelmed with too many orders at once [30, 31].
    3. **Lifecycle**: Use `await queue.join()` to wait until every order in the truck