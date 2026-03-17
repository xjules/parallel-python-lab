import random
import time


STAGE_DURATIONS = {
    "order": 1,
    "ingredients": 2,
    "cook": 3,
    "prepare": 1,
    "customer": 0,
}

def ingredients(order):
    print(f"ingredients working on #{order['id']}")
    time.sleep(STAGE_DURATIONS["ingredients"])
    order["ingredients"] = "ok"
    return order


def cook(order):
    print(f"cook working on #{order['id']}")
    time.sleep(STAGE_DURATIONS["cook"])
    order["cook"] = "ok"
    return order


def prepare(order):
    print(f"prepare working on #{order['id']}")
    time.sleep(STAGE_DURATIONS["prepare"])
    order["prepare"] = "ok"
    return order


def customer(order):
    dt = time.time() - order["start"]
    print(f"served #{order['id']} in {dt:.2f}s")


def order_stage(order_id):
    menu = ["hotdog", "burger", "ice-cream"]
    order = {
        "id": order_id,
        "item": random.choice(menu),
        "start": time.time(),
    }
    time.sleep(STAGE_DURATIONS["order"])
    print(f"New order #{order['id']}: {order['item']}")
    return order


def main():
    for i in range(5):
        order = order_stage(i)
        order = ingredients(order)
        order = cook(order)
        order = prepare(order)
        customer(order)

if __name__ == "__main__":
    main()
