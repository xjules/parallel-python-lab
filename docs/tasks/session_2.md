# Async Food-Truck Factory with multiple workers
---
# Task: Implement async version of the foodtruck

**Goal:** We don't want to wait for the stage to finish

### What to do

- All stages should be async. 
- Try to use asyncio.gather(...). 
- Each task should exit gracefully. We don't want Ctrl+C


---

# Task: Introduce exception

**Goal:** How to handle exception

### What to do

Introduce random exception to the cook stage and handle it.
There should be a random chance that the order gets "burned" in a cook stage

---
# Task introduce PriorityQueue

**Goal:** asyncio.Queue vs asyncio.PriorityQueue

### What to do

Some items might have a higher priority to cook for instance

---
# Task introduce TopicQueue

**Goal:** asyncio.Queue with subscribers on topics

### What to do

Implement centralized broker

---
# Task: Handle cancellation gracefully

**Goal:** Make a key that will cancel all execution

### What to do

catch Cancellation error. 