import asyncio
import os
import threading

NUM_CORES = 30
# A Barrier ensures all 30 threads reach this point before any proceed
sync_barrier = threading.Barrier(NUM_CORES)


async def core_task(core_id):
    """The async workload running on a specific core."""
    # 1. Do some initial async work
    await asyncio.sleep(0.1)

    # 2. Synchronize across all threads/cores
    # We use a thread-safe barrier because asyncio primitives aren't cross-thread safe
    print(f"Core {core_id} (OS PID {os.getpid()}) reaching sync point...")

    # run_in_executor allows us to call the blocking barrier without freezing this loop
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, sync_barrier.wait)

    # 3. All cores proceed at once
    print(f"Core {core_id} synchronized and proceeding!")


def start_loop_in_thread(core_id):
    """Entry point for each thread to set up its own event loop."""
    asyncio.run(core_task(core_id))


# Launch 30 threads
threads = []
for i in range(NUM_CORES):
    t = threading.Thread(target=start_loop_in_thread, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("All cores finished.")
