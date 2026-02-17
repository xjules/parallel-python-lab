import random
import time


def ingredients(order):
    print(f"🥕 ingredients working on #{order['id']}")
    time.sleep(2)
    order["ingredients"] = "ok"
    return order


def cook(order):
    print(f"🔥 cook working on #{order['id']}")
    time.sleep(3)
    order["cook"] = "ok"
    return order


def prepare(order):
    print(f"📦 prepare working on #{order['id']}")
    time.sleep(1)
    order["prepare"] = "ok"
    return order


def customer(order):
    dt = time.time() - order["start"]
    print(f"🎉 served #{order['id']} in {dt:.2f}s")


def producer(order_id):
    menu = ["🌭 hotdog", "🍔 burger", "🍦 ice-cream"]
    order = {
        "id": order_id,
        "item": random.choice(menu),
        "start": time.time(),
    }
    time.sleep(1)
    print(f"\n📝 new order #{i}: {order['item']}")


def main():
    for i in range(5):
        order = producer(i)
        order = ingredients(order)
        order = cook(order)
        order = prepare(order)
        customer(order)


# do async await vs gather
# -- do parameters,  except asyncio.CancelledError:
# exception handling in async tasks, cancellation, timeouts, TaskGroups
# do async wait vs creat_task
# do async TaskGroup (Python 3.11+)
# do async synchronization primitives (locks, events, queues, futures)
# free threaded python https://astral.sh/blog/python-3.14
# check this - do full CPU parallelism with multiple interpreters (no GIL) https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.InterpreterPoolExecutor
# from concurrent.futures import InterpreterPoolExecutor

# def process_data(data):
#     # Each interpreter has its own isolated memory and state
#     return sum(data) / len(data)

# with InterpreterPoolExecutor(max_workers=4) as executor:
#     results = list(executor.map(process_data, [range(1000), range(2000)]))
# independent interpreters, no GIL, true parallelism for CPU-bound tasks

# subinterpreters (Python 3.13+) https://docs.python.org/3/library/subinterpreter.html

# do asyncio.to_thread (sync2async)
# diagram event loop, tasks, threads
# import sys
# Returns True if the GIL is active, False if running in free-threaded mode
# print(sys._is_gil_enabled())

if __name__ == "__main__":
    main()
