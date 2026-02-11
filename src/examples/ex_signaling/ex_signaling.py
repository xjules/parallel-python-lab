import asyncio
import random
import time


class Stage:
    def __init__(self, name, in_q, out_q, seconds, worker_id=None):
        self.name = name
        self.in_q = in_q
        self.out_q = out_q
        self.seconds = seconds
        self.worker_id = worker_id

    async def run(self, closing_time: asyncio.Event):
        while True:
            if closing_time.is_set() and self.in_q.empty():
                print(
                    f"🧹 {self.name}[{self.worker_id}] goes home (closed + empty queue)"
                )
                return

            try:
                # Don't block forever, so we can re-check closing_time.
                order = await asyncio.wait_for(self.in_q.get(), timeout=0.5)
            except asyncio.TimeoutError:
                continue

            print(f"{self.name} worker {self.worker_id} working on {order=}")
            await asyncio.sleep(self.seconds + random.random() * self.seconds)
            order[self.name] = "ok"
            await self.out_q.put(order)


class Producer:
    def __init__(self, out_q, n_orders=10):
        self.out_q = out_q
        self.menu = ["🌭 hotdog", "🍔 burger", "🍦 ice-cream"]
        self.n_orders = n_orders

    async def run(self, closing_time: asyncio.Event):
        for i in range(self.n_orders):
            order = {"id": i, "item": random.choice(self.menu), "start": time.time()}
            print(f"new f{order=}")
            await self.out_q.put(order)
            await asyncio.sleep(random.random() * 4)
        closing_time.set()


class Customer:
    def __init__(self, in_q):
        self.in_q = in_q

    async def run(self, closing_time: asyncio.Event):
        while True:
            if closing_time.is_set() and self.in_q.empty():
                print("🏁 customer leaves (closed + no pending orders)")
                return
            try:
                order = await asyncio.wait_for(self.in_q.get(), timeout=0.5)
            except asyncio.TimeoutError:
                continue
            dt = time.time() - order["start"]
            print(f"✅ order {order['id']} took {dt:.2f}s")


N_workers = 3


async def main():
    q_order = asyncio.Queue()
    q_ing = asyncio.Queue()
    q_cook = asyncio.Queue()
    q_prep = asyncio.Queue()

    closing_time = asyncio.Event()

    producer = Producer(q_order)

    ingredients_workers = [
        Stage("ingredients", q_order, q_ing, 3, worker_id=wid)
        for wid in range(N_workers)
    ]
    cook_workers = [
        Stage("cook", q_ing, q_cook, 3, worker_id=wid) for wid in range(N_workers)
    ]
    prep_workers = [
        Stage("prepare", q_cook, q_prep, 3, worker_id=wid) for wid in range(N_workers)
    ]

    customer = Customer(q_prep)

    await asyncio.gather(
        producer.run(closing_time),
        *[w.run(closing_time) for w in ingredients_workers],
        *[w.run(closing_time) for w in cook_workers],
        *[w.run(closing_time) for w in prep_workers],
        customer.run(closing_time),
    )


if __name__ == "__main__":
    asyncio.run(main())
