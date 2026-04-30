import time
import os
from config import MINECRAFT_PATH
from play import create_world
from rich.console import Console

REPLAY_PATH = MINECRAFT_PATH + "/mcsrranked/replay"
WORLD_PATH = MINECRAFT_PATH + "/saves/seedscraper"
LOG_PATH = MINECRAFT_PATH + "/logs/latest.log"
IGT_PATH = WORLD_PATH + "/speedrunigt/record.json"

console = Console()
with console.status("[bold cyan]Creating world...", spinner_style="bold cyan") as status:
    for j in range(3, 0, -1):
        status.update(f"Creating world in [bold cyan]{j}[/]...")
        time.sleep(1)

def wait_for_world_exit():
    with open(LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            if "left the game" in line:
                time.sleep(1.5)
                return True

while True:
    create_world(None, True)
    wait_for_world_exit()

