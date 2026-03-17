import asyncio
import random
import time


def heavy_cook_work(order, n) -> int:
    total = 0
    for i in range(n):
        total += i * i
    order["heavy_cook_work"] = total
    return order


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
        await self.out_q.put(order)

    async def run(self):
        while True:
            order = await self.in_q.get()
            if order is None:
                await self.out_q.put(None)
                self.in_q.task_done()
                return

            await self.handle(order)
            self.in_q.task_done()


class IngredientsStage(Stage):
    async def handle(self, order):
        if order.get("kind") == "new_order":
            await self.process(order)
            order[self.name] = "ok"
            await self.out_q.put(order)

        if order.get("kind") == "extra_spice_request":
            print(f"{self.name} ordering extra spice for order {order['id']}")
            await asyncio.sleep(self.seconds + random.random() * self.seconds)
            order["spice_ready"] = True
            print(f"{self.name}: spice ready for order {order['id']}")
            await self.out_q.put(order)


class CookStage(Stage):
    def __init__(self, name, in_q, out_q, seconds, sem, ingredients_req_q):
        super().__init__(name, in_q, out_q, seconds)
        self.sem = sem
        self.ingredients_req_q = ingredients_req_q

    async def handle(self, order):
        async with self.sem:
            print(f"{self.name} working on order {order['id']} type={order['type']}")
            if order["type"] == "extra_ing":
                ok_spice = order.get("spice_ready", False)
                if not ok_spice:
                    print(f"{self.name}: order {order['id']} needs extra spice")
                    order["kind"] = "extra_spice_request"
                    await self.ingredients_req_q.put(order)
                    return
                else:
                    order["kind"] = "fast"

            if order["type"] == "fast":
                await asyncio.sleep(self.seconds + random.random() * self.seconds)

            elif order["type"] == "heavy":
                # TODO compare GIL with No GIL python!
                order = await asyncio.to_thread(heavy_cook_work, order, 8_000_000)
                # TODO do something else instead!
            else:
                raise RuntimeError(f"unknown order type: {order['type']}")

            print(f"{self.name}: order {order['id']}")
            order[self.name] = "ok"
            order["kind"] = "cooked"
            await self.out_q.put(order)


class OrderStage:
    def __init__(self, out_q, n_orders=10):
        self.out_q = out_q
        self.n_orders = n_orders
        self.menu = [
            ("burger", "fast"),
            ("smoked_ribs", "heavy"),
            ("soup", "extra_ing"),
        ]

    async def run(self):
        for i in range(self.n_orders):
            item, kind = random.choice(self.menu)
            order = {
                "id": i,
                "item": item,
                "type": kind,
                "kind": "new_order",
                "start": time.time(),
            }
            print(f"new {order=}")
            await self.out_q.put(order)
            await asyncio.sleep(random.random() * 4)

        await self.out_q.put(None)


class Customer:
    def __init__(self, in_q):
        self.in_q = in_q
        self.done = 0

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

    q_order = asyncio.Queue(maxsize=5)
    q_cook = asyncio.Queue()
    q_prep = asyncio.Queue()
    q_done = asyncio.Queue()

    cook_sem = asyncio.Semaphore(n_stations)

    producer = OrderStage(q_order, n_orders=10)
    ingredients = IngredientsStage("ingredients", q_order, q_cook, 1.0)

    cooks = [
        CookStage("cook", q_cook, q_prep, 2.0, cook_sem, q_order)
        for _ in range(n_cooks)
    ]
    prep = Stage("prepare", q_prep, q_done, 1.0)
    customer = Customer(q_done)

    async with asyncio.TaskGroup() as tg:
        # TODO make gracefull shutdown
        tg.create_task(producer.run())
        tg.create_task(ingredients.run())
        tg.create_task(prep.run())
        for w in cooks:
            tg.create_task(w.run())
        tg.create_task(customer.run())


if __name__ == "__main__":
    asyncio.run(main())
