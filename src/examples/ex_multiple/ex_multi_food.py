import asyncio
import random
import time


class Stage:
    def __init__(self, name, in_q, out_q, seconds, id_worker=None):
        self.name = name
        self.in_q = in_q
        self.out_q = out_q
        self.seconds = seconds
        self.id_worker = id_worker

    async def run(self):
        while True:
            order = await self.in_q.get()
            if order is None:
                await self.out_q.put(None)
                return
            print(f"{self.name} worker {self.id_worker} working on {order=}")
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


N_workers = 3


async def main():
    q_order = asyncio.Queue()
    q_ing = asyncio.Queue()
    q_cook = asyncio.Queue()
    q_prep = asyncio.Queue()

    producer = Producer(q_order)

    ingredients_workers = [
        Stage("ingredients", q_order, q_ing, 3, id_worker=wid)
        for wid in range(N_workers)
    ]
    cook_workers = [
        Stage("cook", q_ing, q_cook, 3, id_worker=wid) for wid in range(N_workers)
    ]
    prep_workers = [
        Stage("prepare", q_cook, q_prep, 3, id_worker=wid) for wid in range(N_workers)
    ]

    customer = Customer(q_prep)

    await asyncio.gather(
        producer.run(),
        producer.run(),
        *[w.run() for w in ingredients_workers],
        *[w.run() for w in cook_workers],
        *[w.run() for w in prep_workers],
        customer.run(),
    )


if __name__ == "__main__":
    asyncio.run(main())
