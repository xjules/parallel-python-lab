---
marp: true
theme: dracula
class: invert
paginate: true
size: 16:9

---

# Concurrency
- Allowing more than one task to be handled at the same time
    - broader term than parallelism, suggesting that multiple tasks have the ability to run in an **overlapping manner**
- We **switch** between tasks
    - baker starts a second cake while the first is in owen
- Concurrency is about *managing* many things at once, but not necessarily *doing* them at the exact same instant.

---

# Parallelism
- Executing multiple operations at the **exact same time**
- Concurrency can happen on a single-core CPU via "time slicing," true parallelism **requires a CPU / GPU with multiple cores**.
    - Two distinct bakers working on two different cakes simultaneously
- Parallelism implies concurrency, but concurrency does not always imply parallelism [5].

---

# Understanding the Bottlenecks
- I/O-Bound
    - The application spends most of its time waiting on a **network, disk, or other I/O device**
    - Downloading web pages, querying a database, or reading files

- CPU-Bound
    - The application is limited by the **clock speed and cores of the CPU**
    - Mathematical computations, image processing, or looping over large datasets

---

# What is GIL?
- **Global Interpreter Lock**
    - mechanism that prevents one Python process from executing more than one Python bytecode instruction at any given time
    - even on a multi-core machine, a standard Python process can only have **one thread running Python code at a time**
- This makes standard multithreading ineffective for speeding up CPU-bound tasks

---

# Why is GIL Needed?
- GIL exists primarily because of how **CPython manages memory**:
    - **Reference Counting**: 
        - Python tracks how many places reference an object. 
        - When the count reaches zero, the object is deleted
        - **not thread-safe**, without GIL, two threads could increment a reference count simultaneously, leading to memory leaks or application crashes
    - GIL serves as a "safety net" to prevent these raise conditions

---

# When is GIL Released?
- The GIL is not held forever. It is released during **I/O operations**.
    - Low-level system calls for I/O happen outside the Python runtime.
    - This allows Python to employ **Multithreading** or **Asyncio** to handle many I/O-bound tasks concurrently
- **Note**: For CPU-bound Python code, the GIL remains locked, necessitating other models like **Multiprocessing** / **Free-Threaded (No-GIL) Python** for true parallelism

---
# Summary
- Multiprocessing / Free threaded python
    - True parallelism
    - Ideal for CPU-bound workloads
- Multithreading
    - Shared memory, concurrent execution
    - Best for I/O-bound workloads, limited by GIL for CPU work
- Asyncio
    - Cooperative multitasking, tasks yield control explicitly
    - Single-threaded, Massive I/O concurrency