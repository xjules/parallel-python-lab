import asyncio
import random
import time
from datetime import datetime


class Stage:
    def __init__(self, name, in_q, out_q, seconds):
        self.name = name
        self.in_q = in_q
        self.out_q = out_q
        self.seconds = seconds

    async def do_work(self, order):
        print(
            f"{self.name} started on {order["id"]} at time {datetime.now().strftime("%H:%M:%S")}"
        )
        await asyncio.sleep(self.seconds + random.random() * self.seconds)
        order[self.name] = "ok"
        print(
            f"{self.name} finished on {order["id"]} at time {datetime.now().strftime("%H:%M:%S")}"
        )
        return order

    async def run(self):
        while True:
            order = await self.in_q.get()
            order = await self.do_work(order)
            await self.out_q.put(order)


async def main():
    q_order = asyncio.Queue()
    q_ing = asyncio.Queue()
    q_cook = asyncio.Queue()
    q_prep = asyncio.Queue()
    q_done = asyncio.Queue()

    stages = [
        Stage("ingredients", q_order, q_ing, 2.8),
        Stage("cook", q_ing, q_cook, 3.2),
        Stage("prepare", q_cook, q_done, 3.6),
    ]

    tasks = [asyncio.create_task(s.run()) for s in stages]

    async def do_orders():
        menu = ["hotdog", "hamburger", "ice-cream"]
        for i in range(10):
            await q_order.put(
                {"id": i, "item": random.choice(menu), "start": time.time()}
            )
            await asyncio.sleep(0.3)  # new customers arrive
        await q_order.put(None)  # stop signal

    async def do_customers():
        while True:
            order = await q_done.get()
            if order is None:
                return
            print(
                f"✅ order {order['id']} ({order['item']}) took {time.time() - order['start']:.2f}s"
            )

    asyncio.gather(do_orders(), do_customers())

    for t in tasks:
        t.cancel()


if __name__ == "__main__":
    asyncio.run(main())
