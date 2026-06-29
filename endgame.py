import time
import os
from config import MINECRAFT_PATH
from play import create_world, wait_for_world_exit
from rich.console import Console

console = Console()
with console.status("[bold cyan]Creating world...", spinner_style="bold cyan") as status:
    for j in range(3, 0, -1):
        status.update(f"Creating world in [bold cyan]{j}[/]...")
        time.sleep(1)

while True:
    create_world(None, True)
    wait_for_world_exit()

