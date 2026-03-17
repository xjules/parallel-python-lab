import asyncio
import os
import threading

NUM_CORES = 30
sync_barrier = threading.Barrier(NUM_CORES)


async def core_task(core_id):
    await asyncio.sleep(0.1)
    print(f"Core {core_id} (OS PID {os.getpid()}) reaching sync point...")

    # run_in_executor can block the barrier without freezing this loop
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, sync_barrier.wait)
    print(f"Core {core_id} synchronized and proceeding!")


def start_loop_in_thread(core_id):
    # each thread runs its own event loop
    asyncio.run(core_task(core_id))


threads = []
for i in range(NUM_CORES):
    t = threading.Thread(target=start_loop_in_thread, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("All cores finished.")
