---
marp: true
theme: dracula
class: invert
paginate: true
size: 16:9
---

# Concurrency vs Parallelism

Modern simulation systems must:

- Handle many independent jobs
- Mix I/O and heavy computation
- Scale across cores and machines

Before coding → understand the execution model.

---

# The Three Pillars

## 1️⃣ Multiprocessing
- True parallelism
- Separate processes
- Separate memory spaces
- Ideal for CPU-bound workloads

---

## 2️⃣ Multithreading
- Shared memory
- Concurrent execution
- Best for I/O-bound workloads
- Limited by the GIL for CPU work

---

## 3️⃣ Asyncio
- Single-threaded
- Cooperative multitasking
- Tasks yield control explicitly
- Massive I/O concurrency

---

# I/O-Bound vs CPU-Bound

## CPU-Bound
- Heavy numerical computation
- Image processing
- Simulations
- Large matrix ops

→ Use **Multiprocessing**

---

## I/O-Bound
- Network requests
- File reads/writes
- Database queries
- APIs / WebSockets

→ Use **Asyncio**

---

# The Global Interpreter Lock (GIL)

- Only one thread executes Python bytecode at a time
- Threads do NOT provide true CPU parallelism
- Designed for memory safety
- Major reason multiprocessing exists

---

# Summary

| Model | Parallel? | Best For |
|-------|-----------|----------|
| Threads | ❌ (CPU) | I/O |
| Asyncio | ❌ | High-concurrency I/O |
| Processes | ✅ | CPU workloads |

Understand this before writing architecture.