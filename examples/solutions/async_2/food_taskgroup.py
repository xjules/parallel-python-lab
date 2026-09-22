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


global_closed_cooks = 0
n_cooks = 3
class Stage:
    def __init__(self, name, in_q, out_q):
        self.name = name
        self.in_q = in_q
        self.out_q = out_q

    async def process(self, order):
        print(f"{self.name} working on order {order['id']}")
        await asyncio.sleep(STAGE_DURATIONS[self.name])

    async def handle(self, order):
        await self.process(order)
        order[self.name] = "ok"
        await self.out_q.put(order)

    async def run(self):
        while True:
            try:
                order = await self.in_q.get()
            except asyncio.QueueShutDown:
                if self.name == "cook":
                    global global_closed_cooks
                    print(f"Closing cook stage {global_closed_cooks}")
                    global_closed_cooks += 1
                    if global_closed_cooks == n_cooks:
                        self.out_q.shutdown()
                else:
                    self.out_q.shutdown()
                return


            try:
                # TODO make if this takes too long, the order failed
                await self.handle(order)
            except Exception as e:
                print(f"{self.name} failed on order {order['id']}: {e}")
                # TODO propagate failure to customer and redo the order
                order[self.name] = "failed"
                await self.out_q.put(order)
            finally:
                self.in_q.task_done()


class CookStage(Stage):
    def __init__(self, name, in_q, out_q, sem):
        super().__init__(name, in_q, out_q)
        self.sem = sem

    async def process(self, order):
        async with self.sem:
            print(f"{self.name} working on order {order['id']}")
            await asyncio.sleep(STAGE_DURATIONS[self.name])

            # if random.random() < 0.25:
            #     raise RuntimeError("burned order")


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
            await asyncio.sleep(STAGE_DURATIONS["order"])
        print("No more orders, shutting down")
        self.out_q.shutdown()


class Customer:
    def __init__(self, in_q):
        self.in_q = in_q

    async def run(self):
        while True:
            try:
                order = await self.in_q.get()
            except asyncio.QueueShutDown:
                 return

            if order is None:
                self.in_q.task_done()
                return

            dt = time.time() - order["start"]
            print(f"order {order['id']} took {dt:.2f}s -> {order}")
            self.in_q.task_done()

async def monitor_all_tasks():
    while True:
        tasks = asyncio.all_tasks()
        print(f"Running tasks: {[t.get_name() for t in tasks]}")
        await asyncio.sleep(1)

async def main():
    n_stations = 2

    q_order = asyncio.Queue(maxsize=5)  # limited size
    # TODO asyncio.Queue vs asyncio.PriorityQueue
    q_ing = asyncio.Queue()
    q_cook = asyncio.Queue()
    q_prep = asyncio.Queue()

    cook_sem = asyncio.Semaphore(n_stations)

    producer = OrderStage(q_order, n_orders=4)

    ingredients = Stage("ingredients", q_order, q_ing)
    cooks = [CookStage("cook", q_ing, q_cook, cook_sem) for _ in range(n_cooks)]
    prep = Stage("prepare", q_cook, q_prep)

    customer = Customer(q_prep)

    async with asyncio.TaskGroup() as tg:
        # TODO print number of orders in the process
        tg.create_task(producer.run(), name="producer")
        tg.create_task(ingredients.run(), name="ingredients")
        tg.create_task(prep.run(), name="prep")
        for i, w in enumerate(cooks):
            tg.create_task(w.run(), name=f"cook-{i}")
        tg.create_task(customer.run(), name="customer")
        tg.create_task(monitor_all_tasks(), name="monitor")


if __name__ == "__main__":
    asyncio.run(main())
