---
marp: true
theme: dracula
class: invert
paginate: true
size: 16:9

---

# `async` Streams
- `asyncio.start_server`
  - create and manage servers in `asyncio` without interacting with raw sockets
  - `host`, `port`, and the callback which 
  - Connection Callback 
    - coroutine (`client_connected_cb`) that is triggered automatically whenever a client connects
    - receives a `StreamReader` and `StreamWriter`

---

# `StreamReader`
- Provides a high-level API to read bytes from a network stream
- Non-blocking coroutines 
    - `readline()`- waits for a full line
    - `read(n)` - waits for a specific number of bytes
- **EOF Handling**: The reader signals the end of the stream when no more data is available, typically returning an empty byte string

---

# `StreamWriter`
- Manages the transmission of data to the socket buffer
- Functions 
   - `drain()` coroutine - critical for flow control. 
   - `write()` is a regular method that only adds data to an internal queue, we must call `await writer.drain()` to wait until the buffer is flushed
- **Cleanup**: Proper termination requires calling `writer.close()` followed by `await writer.wait_closed()` to ensure resources are fully released

---
# Decoupling with `asyncio.Queue`
- **Producer-Consumer Pattern**: decouples data generation from data processing
- **FIFO Logic**
- **Concurrency Control**: A queue allows multiple workers to pull items greedily and process them concurrently without direct interaction with producers
- Functions:
    - **Producers**: `put()` (blocks if queue is full) or `put_nowait()`
    - **Consumers**: `get()` (blocks if queue is empty) or `get_nowait()`

---

# Flow Control and Synchronization
- `maxsize` limits how many items the queue can hold
- **Lifecycle Tracking**:
    - `task_done()`: Signals the queue that a formerly enqueued task is complete [11].
    - `join()`: A coroutine that blocks until all items in the queue have been processed and marked with `task_done()`
- **Specialized Variants**: 
    - `PriorityQueue`: Retrieves items in priority order (lowest value first)
    - `LifoQueue`: A stack-based **Last-In, First-Out** structure

---

# Fast async communication `pyzmq`
- `pyzmq` provides bindings for ZeroMQ, a high-performance asynchronous messaging library.
- native `asyncio` implementation that allows to `await` on socket events 
    - `await socket.recv()`
- Unlike RabbitMQ, ZeroMQ is often brokerless, allowing direct peer-to-peer communication between microservices.

---

# Messaging Patterns
- **REQ/REP**: A classic synchronous pattern for request and response cycles between a client and a server.
- **PUB/SUB**: A pattern for one-to-many communication where subscribers filter messages from a publisher.
- **PUSH/PULL**: Ideal for distributing work among a cluster of workers (parallel pipelines)
- **ROUTER/DEALER**: custom one-to-one communication
- Multiple patterns can be combined to build complex distributed architectures.

---

# Reliability & Performance
- ZeroMQ sockets automatically handle reconnections if a service goes down and comes back up
- It handles message framing; ie. a whole message instead of arbitrary chunks of bytes
- Implemented in **C++**, it is significantly faster than standard HTTP/REST for internal microservice communication.

---

# Async file operations `aiofiles`
- Standard Python file operations (eg., `open().read()`) are blocking and will halt the entire `asyncio` event loop
- `aiofiles` is a utility library that wraps Python's native file API to make it compatible with `async` and `await`
- It is essential when our application must handle massive concurrency while reading from or writing to the local filesystem

---

# IO on files
- `async with aiofiles.open(...)` to ensure files are closed properly.
- coroutines `.read()` and `.write()` must be awaited.
    - While one task is waiting for a slow disk hit, the event loop can switch to a network task or another file operation.

---
### Moving to the Network: Sockets
* **Standard Sockets**: By default, sockets are **blocking**. When waiting for a client to send data, the entire thread stops [1, 2].
* **Non-blocking Sockets**: These return immediately. If no data is ready, they signal the application to "try again later" [2, 3].
* **The Async Way**: `asyncio` uses the OS event notification systems (**epoll**, **kqueue**) to watch these sockets efficiently, waking up your tasks only when data arrives [4, 5].

---

# I/O with `aiohttp`
- `aiohttp` is an asynchronous HTTP client that uses non-blocking sockets all the way down
- make use `async with ClientSession()` to manage connection pooling and ensure resources are cleaned up properly
    * *Foodtruck Context*: Before cooking, your stage might "await" a check to an external Nutritional API via `aiohttp`

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

---

# postgress `asyncpg`
- `asyncpg` uses non-blocking sockets to connect and run queries against PostgreSQL asynchronously
- Every query returns a coroutine, it allows the event loop to manage multiple SQL operations simultaneously

---

# Connection Pooling
- A single database connection can only process one query at a time
- `asyncpg.create_pool` with `min_size` and `max_size` parameters to maintain a cache of pre-established connections
- `async with pool.acquire() as connection:` to retrieve a connection from the pool and automatically release it when finished
- up-scaling: concurrent query execution via pooling can make applications significantly faster than serial execution

---

### Part 3: Transactions & Cursors
* **ACID Integrity**: Transactions are managed using the `connection.transaction()` asynchronous context manager [17].
* **Automatic Rollback**: If an exception occurs within the `async with` block, the transaction is automatically rolled back to maintain consistency [17, 18].
* **Streaming Result Sets**: For large datasets that don't fit in memory, `connection.cursor()` returns an **asynchronous generator** to stream rows one by one [19, 20].
* **Syntax**: These cursors are iterated using `async for` loops [19, 20].