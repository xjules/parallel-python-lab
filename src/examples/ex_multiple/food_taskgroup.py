import asyncio
import random
import time


class Stage:
    def __init__(self, name, in_q, out_q, seconds, fail_prob=0.0):
        self.name = name
        self.in_q = in_q
        self.out_q = out_q
        self.seconds = seconds
        self.fail_prob = fail_prob

    async def run(self, wid: int):
        try:
            while True:
                order = await self.in_q.get()
                print(f"{self.name}[{wid}] working on order {order['id']}")
                await asyncio.sleep(self.seconds)

                # Inject a failure in cook
                if self.fail_prob and random.random() < self.fail_prob:
                    raise RuntimeError(
                        f"{self.name}[{wid}] burned order {order['id']} 🔥"
                    )

                order[self.name] = "ok"
                await self.out_q.put(order)

        except asyncio.CancelledError:
            print(f"🛑 {self.name}[{wid}] cancelled (shutdown cascade)")
            raise


class Producer:
    def __init__(self, out_q, n_orders=50):
        self.out_q = out_q
        self.n_orders = n_orders

    async def run(self):
        for i in range(self.n_orders):
            await self.out_q.put({"id": i, "start": time.time()})
            await asyncio.sleep(0.2)


class Customer:
    def __init__(self, in_q):
        self.in_q = in_q

    async def run(self):
        try:
            while True:
                order = await self.in_q.get()
                dt = time.time() - order["start"]
                print(f"✅ served order {order['id']} in {dt:.2f}s")
        except asyncio.CancelledError:
            print("🛑 customer cancelled (shutdown cascade)")
            raise


async def main():
    q_order = asyncio.Queue()
    q_ing = asyncio.Queue()
    q_cook = asyncio.Queue()
    q_prep = asyncio.Queue()

    producer = Producer(q_order)

    ing = Stage("ingredients", q_order, q_ing, seconds=0.6)
    cook = Stage(
        "cook", q_ing, q_cook, seconds=1.0, fail_prob=0.12
    )  # <-- failure injected
    prep = Stage("prepare", q_cook, q_prep, seconds=0.5)
    customer = Customer(q_prep)

    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(producer.run())

            for i in range(2):
                tg.create_task(ing.run(i))
            for i in range(2):
                tg.create_task(cook.run(i))
            for i in range(2):
                tg.create_task(prep.run(i))

            tg.create_task(customer.run())

    except* RuntimeError as eg:
        # ExceptionGroup handling (Python 3.11+)
        print("\n💥 TaskGroup failed. Exceptions collected:")
        for e in eg.exceptions:
            print("  -", e)


if __name__ == "__main__":
    asyncio.run(main())
