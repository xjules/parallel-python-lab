import asyncio
import random
import time

import numpy as np
from numba import njit


@njit
def cook_kernel(x):
    acc = 0.0
    for i in range(x.size):
        v = x[i]
        acc += (v * v + 0.001) ** 0.5
        x[i] = v * 1.000001
    return acc


class Stage:
    def __init__(self, name, in_q, out_q, seconds):
        self.name = name
        self.in_q = in_q
        self.out_q = out_q
        self.seconds = seconds

    async def run(self):
        while True:
            order = await self.in_q.get()
            if order is None:
                await self.out_q.put(None)
                return
            print(f"{self.name} working on {order=}")
            if self.name == "cook":
                order["x"] = np.random.random(200_000).astype(np.float64)
                score = await asyncio.to_thread(cook_kernel, order["x"])
                order["cook_score"] = score
            await asyncio.sleep(self.seconds + random.random() * self.seconds)
            order[self.name] = "ok"
            await self.out_q.put(order)


class Producer:
    def __init__(self, out_q, n_orders=10):
        self.out_q = out_q
        self.menu = ["🌭 hotdog", "🍔 burger", "🍦 ice-cream"]
        self.n_orders = n_orders

    async def run(self):
        for i in range(self.n_orders):
            order = {"id": i, "item": random.choice(self.menu), "start": time.time()}
            print(f"new f{order=}")
            await self.out_q.put(order)
            await asyncio.sleep(random.random() * 4)
        await self.out_q.put(None)


class Customer:
    def __init__(self, in_q):
        self.in_q = in_q

    async def run(self):
        while True:
            order = await self.in_q.get()
            if order is None:
                return
            dt = time.time() - order["start"]
            print(f"✅ order {order['id']} took {dt:.2f}s")


async def main():
    q_order = asyncio.Queue()
    q_ing = asyncio.Queue()
    q_cook = asyncio.Queue()
    q_prep = asyncio.Queue()

    producer = Producer(q_order)

    ingredients = Stage("ingredients", q_order, q_ing, 3)
    cook = Stage("cook", q_ing, q_cook, 4)
    prepare = Stage("prepare", q_cook, q_prep, 3)

    customer = Customer(q_prep)

    await asyncio.gather(
        producer.run(),
        ingredients.run(),
        cook.run(),
        prepare.run(),
        customer.run(),
    )


if __name__ == "__main__":
    asyncio.run(main())
