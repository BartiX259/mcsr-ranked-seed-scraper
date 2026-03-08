import time
import os
import shutil
import json
import datetime
import pydirectinput
from rich import print
from rich.console import Console
from rich.progress import Progress
from config import MINECRAFT_PATH, PLAY_SEEDS_FILE, PLAY_SEEDS, LOAD_HOTBAR_BIND

REPLAY_PATH = MINECRAFT_PATH + "/mcsrranked/replay/seed_scraper.rrf"
WORLD_PATH = MINECRAFT_PATH + "/saves/seedscraper"
LOG_PATH = MINECRAFT_PATH + "/logs/latest.log"
IGT_PATH = MINECRAFT_PATH + "/saves/seedscraper/speedrunigt/record.json"

EVENT_MAP = {
    # SpeedrunIGT events
    "enter_nether": "nether",
    "enter_bastion": "bastion",
    "enter_fortress": "fortress",
    "nether_travel_blind": "blind",
    "enter_stronghold": "stronghold",
    "enter_end": "end",
}

STYLES = {
    "overworld":  ("bright_green", "█"),
    "nether":     ("red", "█"),
    "bastion":    ("gold1", "▒"),
    "fortress":   ("dark_red", "▓"),
    "blind":      ("cyan", "█"),
    "stronghold": ("grey70", "▒"),
    "end":        ("purple", "█"),
}

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

def wait_for_world_load():
    with open(LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.2)
                continue
            if "logged in with entity id" in line:
                time.sleep(0.5)
                return True

pydirectinput.PAUSE = 0.02

def create_world(seed, mpk):
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
        pydirectinput.write('seedscraper', interval=0.005)
        progress.advance(task)
        # Adv. seed
        shift_tab(1)
        pydirectinput.press('enter')
        progress.advance(task)
        tab(4)
        pydirectinput.write(seed['overworldSeed'], interval=0.005)
        tab(1)
        progress.advance(task)
        pydirectinput.write(seed['netherSeed'], interval=0.005)
        tab(1)
        progress.advance(task)
        pydirectinput.write(seed['theEndSeed'], interval=0.005)
        tab(2)
        progress.advance(task)
        pydirectinput.press('enter')
        # Switch to creative if using MPK
        tab(2)
        if mpk:
            pydirectinput.press('enter')
            pydirectinput.press('enter')
        # Easy difficulty
        tab(1)
        for i in range(3):
            pydirectinput.press('enter')
        progress.advance(task)
        # Allow cheats
        tab(1)
        if not mpk:
            pydirectinput.press('enter')
        progress.advance(task)
        # Create
        tab(4)
        pydirectinput.press('enter')
        progress.advance(task)
    if mpk:
        print("[[blue bold]INFO[/]] Waiting for world load to use MPK.")
        wait_for_world_load()
        pydirectinput.keyDown(LOAD_HOTBAR_BIND)
        pydirectinput.press('1')
        pydirectinput.keyUp(LOAD_HOTBAR_BIND)
    print("[[green bold]OK[/]] World created.")

def local_splits():
    if not os.path.exists(IGT_PATH):
        print(f"[[red bold]ERROR[/]] Speedrunigt not initialized ({IGT_PATH}).")
        return None
    splits = [(0, "overworld")]
    with open(IGT_PATH, "r") as f:
        data = json.load(f)
        for timeline in data["timelines"]:
            ev = timeline["name"]
            if ev in EVENT_MAP:
                splits.append((timeline["igt"], EVENT_MAP[ev]))
        splits.append((data["final_igt"], "finish"))
    return splits

def print_splits(splits, max_time=None, finished=True):
    (last_igt, last_ev) = splits[-1]
    if max_time is None:
        max_time = last_igt
    width = 70
    remaining = width
    for i in range(len(splits) - 1):
        (igt, ev) = splits[i]
        (next_igt, _) = splits[i+1]
        (color, char) = STYLES[ev]
        char_count = min(remaining, max(1, width * (next_igt - igt) // max_time))
        remaining -= char_count
        print(f"[{color}]{char * char_count}", end="")
    for i in range(remaining + 1):
        print(" ", end="")
    if finished:
        s = (last_igt // 1000) % 60
        m = (last_igt // 1000) // 60
        print(f"{m}:{s:02d}")
    else:
        print("-:-")

print("[[blue bold]INFO[/]] To [cyan bold]watch the pro replay[/] of the current seed, go to mcsr ranked -> my replays, the replay should be [cyan bold]first[/] in the list.")
with open(PLAY_SEEDS_FILE, 'r') as f:
    lines = f.readlines()
i = 0
while i < len(lines):
    line = lines[i]
    try:
        seed = json.loads(line)
    except json.JSONDecodeError:
        print("[[red bold]ERROR[/]] Corrupt line in seeds file, skipping.")
        i += 1
        continue
    if not PLAY_SEEDS.get(seed['type'], False):
        i += 1
        continue
    dt = datetime.datetime.fromtimestamp(seed['date'] / 1000.0)
    readable_date = dt.strftime("%b %d, %Y at %I:%M %p")
    replay_path = os.path.dirname(REPLAY_PATH) + "/seed_scraper_" + str(seed["matchId"]) + ".rrf"
    print("[[green bold]OK[/]] Found seed.")
    if os.path.exists(replay_path):
        os.utime(replay_path, None)
    else:
        print("[[yellow bold]WARN[/]] No replay file for this seed.")
    print(f"[[blue bold]TYPE[/]] [yellow]{seed['type']}")
    print(f"[[blue bold]GAME[/]] ", end="")
    last = len(seed['players']) - 1
    winner = seed['winner']
    for (j, p) in enumerate(seed['players']):
        if j == winner:
            print(f"[green]{p}[/]", end="")
        else:
            print(f"[red]{p}[/]", end="")
        if j != last:
            print(" vs ", end="")
    print(f", {readable_date}")

    while True:
        print("[[blue bold]INFO[/]] The script will sleep for 3 seconds then create this world. Make sure to tab into mcsr ranked during this time.")
        print("[[blue bold]INFO[/]] Make sure to be in the [bold cyan]minecraft main menu[/], not the ranked main menu.")
        print("[dim]Press enter to continue, 'p' to use MPK, 's' to skip this seed.")
        inp = input()
        mpk = False
        if inp == "s":
            break
        elif inp == "p":
            mpk = True

        console = Console()
        with console.status("[bold cyan]Creating world...", spinner_style="bold cyan") as status:
            for j in range(3, 0, -1):
                status.update(f"Creating world in [bold cyan]{j}[/]...")
                time.sleep(1)
        create_world(seed, mpk)
        print("[dim]Press enter after playing to see your splits, 'r' to restart the current seed.")
        inp = input()
        if inp == "r":
            continue
        all_splits = []
        for (j, (p, s)) in enumerate(zip(seed['players'], seed['splits'])):
            all_splits.append((p, s, j == winner))
        sp = local_splits()
        if sp is not None:
            all_splits.append(("You", sp, True))
            max_time = 0
            name_len = 0
            for (name, splits, _) in all_splits:
                t = splits[-1][0]
                if t > max_time:
                    max_time = t
                l = len(name)
                if l > name_len:
                    name_len = l
            for (name, splits, finished) in all_splits:
                print(name, end="")
                print(" " * (name_len - len(name) + 1), end="")
                print_splits(splits, max_time, finished)
            top_splits = all_splits[winner][1]
            for j in range(min(len(sp), len(top_splits)) - 1):
                (igt, ev) = sp[j]
                (next_igt, _) = sp[j+1]
                (top_igt, top_ev) = top_splits[j]
                (next_top_igt, _) = top_splits[j+1]
                if ev != top_ev:
                    print(f"[[yellow bold]WARN[/]] Event mismatch ({ev}, {top_ev})")
                    break
                print(f"[{STYLES[ev][0]}]{ev.capitalize()}[/]", end="")
                print(" " * (11 - len(ev)), end="")
                a = next_igt - igt
                b = next_top_igt - top_igt
                if a > b:
                    console.print(f"{a/b:.2f}x [dim]slower[/]", highlight=False)
                else:
                    console.print(f"{b/a:.2f}x [dim cyan]faster[/]", highlight=False)
        print("[dim]Press enter to find next seed, 'r' to restart the current seed.")
        inp = input()
        if inp == "r":
            continue
        else:
            break

    if os.path.exists(replay_path):
        try:
            os.remove(replay_path)
        except OSError:
            print("[[red bold]ERROR[/]] Could not remove replay file.")
    del lines[i]
    with open(PLAY_SEEDS_FILE, 'w') as f:
        f.writelines(lines)
    print(f"[[green bold]OK[/]] Seed removed from queue. {len(lines)} seeds remaining.")

print("[[yellow bold]WARN[/]] No more seeds, exiting.")


