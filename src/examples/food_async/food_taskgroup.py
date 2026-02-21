import asyncio
import random
import time


class Stage:
    def __init__(self, name, in_q, out_q, seconds, worker_id, fail_prob=0.0):
        self.name = name
        self.in_q = in_q
        self.out_q = out_q
        self.seconds = seconds
        self.worker_id = worker_id
        self.fail_prob = fail_prob

    async def run(self):
        try:
            while True:
                order = await self.in_q.get()
                print(f"{self.name}[{self.worker_id}] working on order {order['id']}")
                await asyncio.sleep(self.seconds)

                # Inject a failure in cook
                if self.fail_prob and random.random() < self.fail_prob:
                    raise RuntimeError(
                        f"{self.name}[{self.worker_id}] burned order {order['id']} 🔥"
                    )

                order[self.name] = "ok"
                await self.out_q.put(order)

        except asyncio.CancelledError:
            print(f"🛑 {self.name}[{self.worker_id}] cancelled (shutdown cascade)")
            raise


class Producer:
    def __init__(self, out_q, n_orders=10):
        self.out_q = out_q
        self.menu = ["🌭 hotdog", "🍔 burger", "🍦 ice-cream"]
        self.n_orders = n_orders

    async def run(self):
        for i in range(self.n_orders):
            order = {"id": i, "item": random.choice(self.menu), "start": time.time()}
            print(f"new {order=}")
            await self.out_q.put(order)
            await asyncio.sleep(random.random() * 4)


class Customer:
    def __init__(self, in_q):
        self.in_q = in_q

    async def run(self):
        try:
            while True:
                order = await self.in_q.get()
                dt = time.time() - order["start"]
                print(f"✅ order {order['id']} took {dt:.2f}s")
        except asyncio.CancelledError:
            print("🛑 customer cancelled (shutdown cascade)")
            raise


N_workers = 3


async def main():
    q_order = asyncio.Queue()
    q_ing = asyncio.Queue()
    q_cook = asyncio.Queue()
    q_prep = asyncio.Queue()

    producer = Producer(q_order)

    ingredients_workers = [
        Stage("ingredients", q_order, q_ing, 3, worker_id=wid)
        for wid in range(N_workers)
    ]
    cook_workers = [
        Stage("cook", q_ing, q_cook, 3, worker_id=wid, fail_prob=0.12)
        for wid in range(N_workers)
    ]
    prep_workers = [
        Stage("prepare", q_cook, q_prep, 3, worker_id=wid) for wid in range(N_workers)
    ]

    customer = Customer(q_prep)

    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(producer.run())
            for w in ingredients_workers:
                tg.create_task(w.run())
            for w in cook_workers:
                tg.create_task(w.run())
            for w in prep_workers:
                tg.create_task(w.run())
            tg.create_task(customer.run())

    except* RuntimeError as eg:
        print("\n💥 TaskGroup failed. Exceptions collected:")
        for e in eg.exceptions:
            print("  -", e)


if __name__ == "__main__":
    asyncio.run(main())
