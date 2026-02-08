import asyncio
import time
from collections import defaultdict, deque

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

STAGES = ["ingredients", "cook", "prepare", "customer"]
ICONS = {"ingredients": "🥕", "cook": "🔥", "prepare": "📦", "customer": "🎉"}


async def run_console_viz(events: asyncio.Queue, stop: asyncio.Event) -> None:
    """
    events: queue of dicts like:
      {"type":"enter", "stage":"cook", "id":3, "item":"🍔 burger"}
      {"type":"done",  "id":3, "dt":7.12, "item":"🍔 burger"}
    stop: set when simulation is done
    """
    console = Console()

    # lane -> order_id -> label
    lanes = {s: {} for s in STAGES}
    done = deque(maxlen=12)  # show last completed
    counts = defaultdict(int)
    lat_sum = 0.0

    def render():
        table = Table.grid(expand=True)
        table.add_column(ratio=1)

        # top stats
        total_done = counts["customer"]
        avg = (lat_sum / total_done) if total_done else 0.0
        header = f"🍔 Async Foodtruck  |  completed: {total_done}  |  avg latency: {avg:.2f}s"
        table.add_row(Panel(header, style="bold"))

        # lanes
        for stage in STAGES:
            items = "  ".join(lanes[stage].values()) or "—"
            table.add_row(
                Panel(items, title=f"{ICONS[stage]} {stage}", border_style="cyan")
            )

        # recent done
        recent = "  ".join(done) or "—"
        table.add_row(Panel(recent, title="✅ recently served", border_style="green"))
        return table

    with Live(render(), console=console, refresh_per_second=10) as live:
        while True:
            # Exit when stop is set and no more events are coming in
            if stop.is_set() and events.empty():
                return

            try:
                e = await asyncio.wait_for(events.get(), timeout=0.1)
            except asyncio.TimeoutError:
                live.update(render())
                continue

            et = e.get("type")
            oid = e.get("id")
            item = e.get("item", "")
            label = f"#{oid} {item}".strip()

            if et == "enter":
                stage = e["stage"]
                lanes[stage][oid] = label
                counts[stage] += 1

            elif et == "leave":
                stage = e["stage"]
                lanes[stage].pop(oid, None)

            elif et == "done":
                # remove from all lanes just in case
                for s in STAGES:
                    lanes[s].pop(oid, None)
                dt = float(e.get("dt", 0.0))
                lat_sum += dt
                counts["customer"] += 1
                done.appendleft(f"{label} ({dt:.2f}s)")

            live.update(render())
            events.task_done()
