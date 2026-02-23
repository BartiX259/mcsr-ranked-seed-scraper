import time
import os
import shutil
import json
import datetime
import pydirectinput
from nbt import nbt
from rich import print
from rich.console import Console
from rich.progress import Progress
from config import MINECRAFT_PATH, PLAY_SEEDS_FILE, PLAY_SEEDS

WORLD_PATH = MINECRAFT_PATH + '/saves/seedscraper'

def tab(n):
    for i in range(n):
        pydirectinput.press('tab')
        if i != n - 1:
            time.sleep(0.05)

def shift_tab(n):
    pydirectinput.keyDown('shift')
    time.sleep(0.05)
    tab(n)
    pydirectinput.keyUp('shift')

pydirectinput.PAUSE = 0.02

def create_world(seed):
    with Progress() as progress:
        task = progress.add_task("[bold magenta]Creating world", total=9)
        if os.path.exists(WORLD_PATH):
            shutil.rmtree(WORLD_PATH)
        time.sleep(0.5)
        progress.advance(task)
        # Singleplayer
        tab(1)
        pydirectinput.press('enter')
        # Create world
        shift_tab(3)
        pydirectinput.press('enter')
        # World name
        pydirectinput.keyDown('ctrl')
        pydirectinput.press('backspace')
        pydirectinput.press('backspace')
        pydirectinput.keyUp('ctrl')
        pydirectinput.write('seedscraper')
        progress.advance(task)
        # Adv. seed
        shift_tab(1)
        pydirectinput.press('enter')
        progress.advance(task)
        tab(4)
        pydirectinput.write(seed['overworldSeed'])
        tab(1)
        progress.advance(task)
        pydirectinput.write(seed['netherSeed'])
        tab(1)
        progress.advance(task)
        pydirectinput.write(seed['theEndSeed'])
        tab(2)
        progress.advance(task)
        pydirectinput.press('enter')
        # Easy difficulty
        tab(3)
        for i in range(3):
            pydirectinput.press('enter')
        progress.advance(task)
        # Allow cheats
        tab(1)
        pydirectinput.press('enter')
        progress.advance(task)
        # Create
        tab(4)
        pydirectinput.press('enter')
        progress.advance(task)
    print("[[green bold]OK[/]] World created.")


with open(PLAY_SEEDS_FILE, 'r') as f:
    for line in f:
        seed = json.loads(line)
        if not PLAY_SEEDS[seed['type']]:
            continue
        dt = datetime.datetime.fromtimestamp(seed['date'] / 1000.0)
        readable_date = dt.strftime("%b %d, %Y at %I:%M %p")
        print("[[green bold]OK[/]] Found seed")
        print(f"[[blue bold]Type[/]] [yellow]{seed['type']}")
        print(f"[[blue bold]Game[/]] [yellow]{seed['players'][0]}[/] vs [yellow]{seed['players'][1]}[/], {readable_date}")

        print("[[blue bold]INFO[/]] The script will sleep for 3 seconds then create this world. Make sure to tab into mcsr ranked during this time.")
        print("[[blue bold]INFO[/]] Make sure to be in the [bold cyan]minecraft main menu[/], not the ranked main menu.")
        print("[dim]Press enter to continue, type 's' to skip this seed.")
        inp = input()
        if inp == "s":
            continue

        console = Console()
        with console.status("[bold cyan]Creating world...", spinner_style="bold cyan") as status:
            for i in range(3, 0, -1):
                status.update(f"Creating world in [bold cyan]{i}[/]...")
                time.sleep(1)
        create_world(seed)
    
    print("[[yellow bold]WARNING[/]] No more seeds, exiting.")


