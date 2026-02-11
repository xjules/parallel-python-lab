import random
import time


def ingredients(order):
    print(f"🥕 ingredients working on #{order['id']}")
    time.sleep(2)
    order["ingredients"] = "ok"
    return order


def cook(order):
    print(f"🔥 cook working on #{order['id']}")
    time.sleep(3)
    order["cook"] = "ok"
    return order


def prepare(order):
    print(f"📦 prepare working on #{order['id']}")
    time.sleep(1)
    order["prepare"] = "ok"
    return order


def customer(order):
    dt = time.time() - order["start"]
    print(f"🎉 served #{order['id']} in {dt:.2f}s")


def producer(order_id):
    menu = ["🌭 hotdog", "🍔 burger", "🍦 ice-cream"]
    order = {
        "id": order_id,
        "item": random.choice(menu),
        "start": time.time(),
    }
    time.sleep(1)
    print(f"\n📝 new order #{i}: {order['item']}")


def main():
    for i in range(5):
        order = producer(i)
        order = ingredients(order)
        order = cook(order)
        order = prepare(order)
        customer(order)


if __name__ == "__main__":
    main()
