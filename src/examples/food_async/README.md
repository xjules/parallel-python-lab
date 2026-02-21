# Exercise: Async Food-Truck Factory with multiple workers

Multiple orders can be in the same stage at once.

# Task: Make graceful exit

**Goal:** We don't want to Ctrl+C

### What to do

Make sure each task will exit


# Task: Introduce create_task 

**Goal:** You want background daemons, cancellation control or dynamic spawning

### What to do

run workers in the backround and cancel the tasks when not needed anymore


# Task: Handle cancellation gracefully

**Goal:** You don't want tasks to raise exceptions

### What to do

catch Cancellation error. 
