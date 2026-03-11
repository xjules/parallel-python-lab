---
marp: true
paginate: true
size: 16:9
theme: dracula
---

# Synchronous programming

- Execution proceeds *step by step*, one instruction at a time.
- One flow of control
- Each function call blocks until it returns
- Deterministic execution order
- No concurrency by default

---

# Example

```python
    for i in range(5):
        order = producer()
        order = ingredients(order)
        order = cook(order)
        order = prepare(order)
        customer(order)
```

Nothing else happens while `cook()` runs.

---
# I/O bound


---
# CPU bound

---
# Global interpreter lock

---

# Sequential control flow

Statements execute strictly **top → bottom**.

- Blocking calls - a function call **owns the thread** until it completes.

---

# Single thread by default
Typical Python program starts with:
- one process
- one thread
- one execution path
- you don’t coordinate tasks — because there’s only one.

---

# Strengths

- Easy to reason about (deterministic order)
- Simple debugging + stack traces
- No race conditions by default

---

# Limitations

- Cannot overlap waiting with useful work
- Idle time during I/O
- Poor utilization of multi-core CPUs
- Doesn’t scale to many independent jobs

```python
load_data()   # waits
compute()     # waits
save_data()   # waits
```