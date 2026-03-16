import asyncio
import random
import time


class Stage:
    def __init__(self, name, in_q, out_q, seconds):
        self.name = name
        self.in_q = in_q
        self.out_q = out_q
        self.seconds = seconds

    async def process(self, order):
        print(f"{self.name} working on order {order['id']}")
        await asyncio.sleep(self.seconds + random.random() * self.seconds)
        print(f"{self.name}: order {order['id']}")

    async def handle(self, order):
        await self.process(order)
        order[self.name] = "ok"
        if self.out_q is not None:
            await self.out_q.put(order)

    async def run(self):
        while True:
            order = await self.in_q.get()

            # TODO this will not handle multiple cooks!
            if order is None:
                await self.out_q.put(None)
                self.in_q.task_done()
                return

            try:
                await self.handle(order)
            except Exception as e:
                print(f"{self.name} failed on order {order['id']}: {e}")
                # TODO propagate failure to customer and redo the order
                order[self.name] = "failed"
                await self.out_q.put(order)
            finally:
                self.in_q.task_done()


class CookStage(Stage):
    def __init__(self, name, in_q, out_q, seconds, sem):
        super().__init__(name, in_q, out_q, seconds)
        self.sem = sem

    async def process(self, order):
        async with self.sem:
            print(f"{self.name} working on order {order['id']}")
            await asyncio.sleep(self.seconds + random.random() * self.seconds)

            if random.random() < 0.25:
                raise RuntimeError("burned order")

            print(f"{self.name}: order {order['id']}")


class OrderStage:
    def __init__(self, out_q, n_orders=10):
        self.out_q = out_q
        self.menu = ["hotdog", "burger", "ice-cream"]
        self.n_orders = n_orders

    async def run(self):
        for i in range(self.n_orders):
            order = {"id": i, "item": random.choice(self.menu), "start": time.time()}
            print(f"new {order=}")
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
                self.in_q.task_done()
                return

            dt = time.time() - order["start"]
            print(f"order {order['id']} took {dt:.2f}s -> {order}")
            self.in_q.task_done()


async def main():
    n_cooks = 3
    n_stations = 2

    q_order = asyncio.Queue(maxsize=5)  # limited size
    q_ing = asyncio.Queue()
    q_cook = asyncio.Queue()
    q_prep = asyncio.Queue()

    cook_sem = asyncio.Semaphore(n_stations)

    producer = OrderStage(q_order, n_orders=10)

    ingredients = Stage("ingredients", q_order, q_ing, 1.5)
    cooks = [CookStage("cook", q_ing, q_cook, 2.0, cook_sem) for _ in range(n_cooks)]
    prep = Stage("prepare", q_cook, q_prep, 1.0)

    customer = Customer(q_prep)

    async with asyncio.TaskGroup() as tg:
        # TODO print number of orders process
        tg.create_task(producer.run())
        tg.create_task(ingredients.run())
        tg.create_task(prep.run())
        for w in cooks:
            tg.create_task(w.run())
        tg.create_task(customer.run())


if __name__ == "__main__":
    asyncio.run(main())
