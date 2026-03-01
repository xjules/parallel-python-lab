import asyncio
import random
from asyncio import StreamReader, StreamWriter

import aiohttp


# --- Chapter 4: External API Integration ---
async def check_inventory(session: aiohttp.ClientSession, item_name: str):
    """Simulates an external web request (Chapter 4 concept)."""
    url = f"https://api.foodtruck.com/inventory/{item_name}"
    # In a real app, you'd await session.get(url)
    await asyncio.sleep(random.random())
    return True


class Stage:
    def __init__(self, name, in_q, out_q, seconds, worker_id, session=None):
        self.name = name
        self.in_q = in_q
        self.out_q = out_q
        self.seconds = seconds
        self.worker_id = worker_id
        self.session = session

    async def run(self):
        while True:
            order = await self.in_q.get()
            if order is None:
                await self.out_q.put(None)
                return

            print(
                f"  [{self.name}-{self.worker_id}] Processing order #{order['id']}: {order['item']}"
            )

            # Chapter 4: Using aiohttp for concurrent I/O in a stage
            if self.session and self.name == "ingredients":
                await check_inventory(self.session, order["item"])

            await asyncio.sleep(self.seconds + random.random())
            order[self.name] = "ok"
            await self.out_q.put(order)
            self.in_q.task_done()  # Chapter 12 concept used for cleanup


# --- Chapter 3: High-Level Server API ---
class FoodTruckServer:
    def __init__(self, order_queue: asyncio.Queue):
        self.order_queue = order_queue
        self.order_id_counter = 0

    async def handle_customer(self, reader: StreamReader, writer: StreamWriter):
        """Callback for asyncio.start_server (Chapter 3)."""
        address = writer.get_extra_info("peername")
        print(f"--- New Connection from {address} ---")

        data = await reader.readline()
        item = data.decode().strip()

        if item:
            order = {
                "id": self.order_id_counter,
                "item": item,
                "start": asyncio.get_event_loop().time(),
            }
            self.order_id_counter += 1
            await self.order_queue.put(order)
            writer.write(f"Order #{order['id']} for {item} received!\n".encode())
            await writer.drain()

        writer.close()
        await writer.wait_closed()


async def main():
    order_q = asyncio.Queue()
    prep_q = asyncio.Queue()
    final_q = asyncio.Queue()

    # Chapter 4: Shared session for external requests
    async with aiohttp.ClientSession() as session:
        # Define workers
        workers = [
            Stage("ingredients", order_q, prep_q, 1, wid, session).run()
            for wid in range(2)
        ] + [Stage("prepare", prep_q, final_q, 2, wid).run() for wid in range(2)]

        # Chapter 3: Starting the server
        ft_server = FoodTruckServer(order_q)
        server = await asyncio.start_server(
            ft_server.handle_customer, "127.0.0.1", 8000
        )

        print("🚚 Food Truck Server running on localhost:8000")
        print("   Order via: 'echo \"🍔 burger\" | nc localhost 8000'")

        # Chapter 4: Managing multiple concurrent long-running tasks
        async with server:
            await asyncio.gather(server.serve_forever(), *workers)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:  # Chapter 3: Simple shutdown handling
        pass
