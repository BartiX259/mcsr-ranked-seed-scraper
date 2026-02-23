import time
import os
import shutil
import json
import datetime
import pydirectinput
from nbt import nbt
from rich import print
from rich.console import Console
from config import PLAY_MINECRAFT_PATH, PLAY_SEEDS_FILE, PLAY_SEEDS

WORLD_PATH = PLAY_MINECRAFT_PATH + '/saves/seedscraper'
LEVEL_DAT_PATH = WORLD_PATH + '/level.dat'
DIM_1_PATH = WORLD_PATH + '/DIM-1'
LOG_FILE_PATH = PLAY_MINECRAFT_PATH + '/logs/latest.log'

def wait_for_world_load():
    with open(LOG_FILE_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            if "logged in with entity id" in line:
                time.sleep(0.2)
                return True
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
    print("The script will sleep for 3 seconds then create this world. Make sure to tab into minecraft in this time (main menu).")
    print("[dim]Press enter to continue")
    input()
    console = Console()
    with console.status("[bold cyan]Creating world...", spinner_style="bold cyan") as status:
        for i in range(3, 0, -1):
            status.update(f"Creating world in [bold cyan]{i}[/]...")
            time.sleep(1)
    if os.path.exists(WORLD_PATH):
        shutil.rmtree(WORLD_PATH)
    time.sleep(0.5)
    # Singleplayer
    tab(1)
    pydirectinput.press('enter')
    # Create world
    shift_tab(2)
    pydirectinput.press('enter')
    # World name
    pydirectinput.keyDown('ctrl')
    pydirectinput.press('backspace')
    pydirectinput.press('backspace')
    pydirectinput.keyUp('ctrl')
    pydirectinput.write('seedscraper')
    # Easy difficulty
    tab(2)
    for i in range(3):
        pydirectinput.press('enter')
    # Allow cheats
    tab(1)
    pydirectinput.press('enter')
    # More world options
    tab(3)
    pydirectinput.press('enter')
    # Seed
    tab(3)
    pydirectinput.write(str(seed['overworldSeed']))
    # Create
    shift_tab(2)
    pydirectinput.press('enter')
    print("World created, waiting for load.")
    wait_for_world_load()
    # Exit
    print("World loaded, exiting")
    pydirectinput.press('esc')
    shift_tab(1)
    pydirectinput.press('enter')
    # Change nether seed
    print("Changing the nether seed")
    time.sleep(1)
    nbtfile = nbt.NBTFile(LEVEL_DAT_PATH,'rb')
    nbtfile["Data"]["WorldGenSettings"]["dimensions"]["minecraft:the_nether"]["generator"]["seed"].value = int(seed['netherSeed'])
    nbtfile["Data"]["WorldGenSettings"]["dimensions"]["minecraft:the_nether"]["generator"]["biome_source"]["seed"].value = int(seed['netherSeed'])
    nbtfile.write_file(LEVEL_DAT_PATH)
    shutil.rmtree(DIM_1_PATH)
    # Play world
    tab(1)
    pydirectinput.press('enter')
    tab(2)
    pydirectinput.press('enter')
    tab(2)
    pydirectinput.press('enter')


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
        create_world(seed)
        break

