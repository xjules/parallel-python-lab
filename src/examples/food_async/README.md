# Exercise: Async Food-Truck Factory with multiple workers

# Task: Make graceful exit

**Goal:** We don't want Ctrl+C

### What to do

Make sure each task will exit


# Task: Introduce exception

**Goal:** How to handle exception

### What to do

Introduce and handle it. You can use gather(...) to decide either to raise or return

# Task introduce PriorityQueue

**Goal:** asyncio.Queue vs asyncio.PriorityQueue

### What to do

Some items might have a higher priority to cook for instance

# Task introduce TopicQueue

**Goal:** asyncio.Queue with subscribers on topics

### What to do

Implement centralized broker


# Task: Introduce create_task 

**Goal:** We want background task, cancellation control and dynamic spawning

### What to do

run workers in the backround and cancel the tasks when not needed anymore


# Task: Handle cancellation gracefully

**Goal:** You don't want tasks to raise exceptions

### What to do

catch Cancellation error. 
