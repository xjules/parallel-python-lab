import asyncio
import random
import time



STAGE_DURATIONS = {
    "order": 1,
    "ingredients": 2,
    "cook": 3,
    "prepare": 1,
    "customer": 0,
}

class Stage:
    def __init__(self, name, in_q, out_q):
        self.name = name
        self.in_q = in_q
        self.out_q = out_q

    async def process(self, order):
        # TODO introduce random exception for the cook stage
        print(f"{self.name} working on order {order['id']}")
        await asyncio.sleep(STAGE_DURATIONS[self.name])

    async def run(self):
        while True:
            # TODO make it exit
            try:
                order = await self.in_q.get()
            except asyncio.QueueShutDown:
                self.out_q.shutdown()  # propagate end signal
                break
            # if order is None:
            #     await self.out_q.put(None)  # propagate end signal
            #     break
            await self.process(order)
            order[self.name] = "ok"
            await self.out_q.put(order)


class OrderStage:
    def __init__(self, out_q, n_orders=2):
        self.out_q = out_q
        self.menu = ["hotdog", "burger", "ice-cream"]
        self.n_orders = n_orders

    async def run(self):
        for i in range(self.n_orders):
            order = {"id": i, "item": random.choice(self.menu), "start": time.time()}
            print(f"new {order=}")
            await self.out_q.put(order)
            await asyncio.sleep(STAGE_DURATIONS["order"])
        # await self.out_q.put(None)  # signal end of orders\
        self.out_q.shutdown()  # signal end of orders
        raise ValueError("Producer done")


class Customer:
    def __init__(self, in_q):
        self.in_q = in_q

    async def run(self):
        while True:
            try:
                order = await self.in_q.get()
            except asyncio.QueueShutDown:
                break
            dt = time.time() - order["start"]
            print(f"order {order['id']} took {dt:.2f}s")


async def main():
    q_order = asyncio.Queue()
    q_ing = asyncio.Queue()
    q_cook = asyncio.Queue()
    q_prep = asyncio.Queue()

    producer = OrderStage(q_order)
    ingredients = Stage("ingredients", q_order, q_ing)
    cook_workers = Stage("cook", q_ing, q_cook)
    prep_workers = Stage("prepare", q_cook, q_prep)
    customer = Customer(q_prep)

    await asyncio.gather(
        producer.run(),
        ingredients.run(),
        cook_workers.run(),
        prep_workers.run(),
        customer.run(),
    )


if __name__ == "__main__":
    asyncio.run(main())
