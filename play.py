import time
import os
import shutil
import json
import datetime
try:
    import pyautogui
except:
    print("No pyautogui")
try:
    import pydirectinput
except:
    print("No pydirectinput")
try:
    import pyscreenrec
except:
    print("No pyscreenrec")
from rich import print, box
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from config import MINECRAFT_PATH, PLAY_SEEDS_FILE, PLAY_SEEDS, LOAD_HOTBAR_BIND, REBIND_TOGGLE_HOTKEY

REPLAY_PATH = os.path.join(MINECRAFT_PATH, "mcsrranked", "replay")
WORLD_PATH = os.path.join(MINECRAFT_PATH, "saves", "seedscraper")
LOG_PATH = os.path.join(MINECRAFT_PATH, "logs", "latest.log")

EVENT_MAP = {
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

RANK_DATA = {
    "coal": {
        "general": {"overworld": 235000, "nether": 65000, "bastion": 345000, "fortress": 190000, "blind": 330000, "stronghold": 185000, "end": 165000},
        "overworld": {"Village": 235000, "Shipwreck": 210000, "Desert Temple": 215000, "Ruined Portal": 108000, "Buried Treasure": None}
    },
    "iron": {
        "general": {"overworld": 221000, "nether": 57000, "bastion": 345000, "fortress": 155000, "blind": 224000, "stronghold": 130000, "end": 145000},
        "overworld": {"Village": 255000, "Shipwreck": 250000, "Desert Temple": 235000, "Ruined Portal": 138000, "Buried Treasure": None}
    },
    "gold": {
        "general": {"overworld": 185000, "nether": 54000, "bastion": 295000, "fortress": 152000, "blind": 195000, "stronghold": 95000, "end": 152000},
        "overworld": {"Village": 230000, "Shipwreck": 225000, "Desert Temple": 198000, "Ruined Portal": 110000, "Buried Treasure": None}
    },
    "emerald": {
        "general": {"overworld": 148000, "nether": 41000, "bastion": 242000, "fortress": 132000, "blind": 138000, "stronghold": 78000, "end": 118000},
        "overworld": {"Village": 177000, "Shipwreck": 163000, "Desert Temple": 164000, "Ruined Portal": 92000, "Buried Treasure": 151000}
    },
    "diamond": {
        "general": {"overworld": 128000, "nether": 37000, "bastion": 202000, "fortress": 114000, "blind": 119000, "stronghold": 57000, "end": 96000},
        "overworld": {"Village": 156000, "Shipwreck": 150000, "Desert Temple": 145000, "Ruined Portal": 82000, "Buried Treasure": 132000}
    },
    "netherite": {
        "general": {"overworld": 117000, "nether": 31000, "bastion": 155000, "fortress": 82000, "blind": 90000, "stronghold": 38000, "end": 62000},
        "overworld": {"Village": 145000, "Shipwreck": 122000, "Desert Temple": 132000, "Ruined Portal": 73000, "Buried Treasure": 115000}
    },
    "pro": {
        "general": {"overworld": 100000, "nether": 31000, "bastion": 155000, "fortress": 85000, "blind": 90000, "stronghold": 39000, "end": 67000},
        "overworld": {"Village": 124000, "Shipwreck": 115000, "Desert Temple": 108000, "Ruined Portal": 62000, "Buried Treasure": 100000}
    }
}

RANKS = ["coal", "iron", "gold", "emerald", "diamond", "netherite", "pro"]

RANK_COLORS = {
    "coal": "grey37",
    "iron": "grey70",
    "gold": "gold1",
    "emerald": "bright_green",
    "diamond": "bright_cyan",
    "netherite": "bright_magenta",
    "pro": "bright_yellow"
}

def get_base_rank_time(rank, split_key, ow_key=None):
    if split_key == "overworld" and ow_key and RANK_DATA[rank]["overworld"].get(ow_key) is not None:
        return RANK_DATA[rank]["overworld"][ow_key]
    return RANK_DATA[rank]["general"].get(split_key, 0)

def format_ms(ms):
    ms = int(ms)
    s = (ms // 1000) % 60
    m = (ms // 1000) // 60
    d = (ms % 1000) // 100
    return f"{m}:{s:02d}.{d}"

def get_rank_and_boundaries(user_time, base_times, delta, pro_time):
    adjusted_times = {}
    for r in RANKS:
        base_val = base_times[r]
        adjusted_times[r] = max(pro_time, base_val - delta)

    midpoints = {}
    for idx in range(len(RANKS) - 1):
        r_curr = RANKS[idx]
        r_next = RANKS[idx+1]
        midpoints[r_curr] = (adjusted_times[r_curr] + adjusted_times[r_next]) / 2

    est_rank = "coal"
    for idx in range(len(RANKS) - 1, 0, -1):
        r_check = RANKS[idx]
        if user_time <= midpoints[RANKS[idx-1]]:
            est_rank = r_check
            break

    to_rank_up = None
    if est_rank != "pro":
        rank_idx = RANKS.index(est_rank)
        to_rank_up = user_time - midpoints[RANKS[rank_idx]]

    return est_rank, to_rank_up, adjusted_times

def generate_splits_table(sp, top_splits, ow_key):
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold white")
    table.add_column("Split", justify="left")
    table.add_column("Your Time", justify="right")
    table.add_column("Est. Split Rank", justify="center")
    table.add_column("To Rank Up", justify="right")
    table.add_column("Seed +/-", justify="center")
    table.add_column("Pro Time", justify="right")
    table.add_column("vs Pro", justify="right")

    total_user_time = 0
    total_pro_time = 0
    adjusted_overall_rank_times = {r: 0 for r in RANKS}
    total_pro_base = 0

    is_run_fully_finished = (sp[-2][1] == "end")

    j = 0
    k = 0
    while j < len(sp) - 1 and k < len(top_splits) - 1:
        (igt, ev) = sp[j]
        (next_igt, _) = sp[j+1]
        (top_igt, top_ev) = top_splits[k]
        (next_top_igt, _) = top_splits[k+1]
        if ev != top_ev:
            k += 1
            continue

        user_split = next_igt - igt
        pro_split = next_top_igt - top_igt

        is_last_split = (j == len(sp) - 2)
        is_split_completed = not (is_last_split and not is_run_fully_finished)

        pro_base = get_base_rank_time("pro", ev, ow_key)
        delta = pro_base - pro_split

        if is_split_completed:
            total_user_time += user_split
            total_pro_time += pro_split
            total_pro_base += pro_base

            base_times = {r: get_base_rank_time(r, ev, ow_key) for r in RANKS}
            est_rank, to_rank_up, adj_times = get_rank_and_boundaries(user_split, base_times, delta, pro_split)

            for r in RANKS:
                adjusted_overall_rank_times[r] += adj_times[r]

            to_rank_up_str = f"+{to_rank_up/1000:.1f}s" if to_rank_up is not None else "-"
            est_rank_display = f"[{RANK_COLORS[est_rank]}]{est_rank.capitalize()}[/]"

            vs_diff = user_split - pro_split
            vs_pro_str = f"[red]+{vs_diff/1000:.1f}s[/]" if vs_diff > 0 else f"[cyan]-{abs(vs_diff)/1000:.1f}s[/]"

            if delta > 0:
                seed_diff_str = f"[cyan]-{delta/1000:.1f}s[/]"
            elif delta < 0:
                seed_diff_str = f"[red]+{abs(delta)/1000:.1f}s[/]"
            else:
                seed_diff_str = "[grey70]0.0s[/]"
        else:
            est_rank_display = "-"
            to_rank_up_str = "-"
            seed_diff_str = "-"
            vs_pro_str = "-"

        split_display = f"[{STYLES[ev][0]}]{ev.capitalize()}[/]"

        table.add_row(
            split_display,
            format_ms(user_split),
            est_rank_display,
            to_rank_up_str,
            seed_diff_str,
            format_ms(pro_split),
            vs_pro_str
        )

        j += 1
        k += 1

    if total_user_time > 0:
        overall_rank, overall_to_rank_up, _ = get_rank_and_boundaries(
            total_user_time, adjusted_overall_rank_times, 0, total_pro_time
        )

        overall_to_rank_up_str = f"+{format_ms(overall_to_rank_up)}" if overall_to_rank_up is not None else "-"

        overall_delta = total_pro_base - total_pro_time
        if overall_delta > 0:
            overall_seed_diff = f"[cyan]-{format_ms(overall_delta)}[/]"
        elif overall_delta < 0:
            overall_seed_diff = f"[red]+{format_ms(abs(overall_delta))}[/]"
        else:
            overall_seed_diff = "[grey70]0.0s[/]"

        overall_vs_diff = total_user_time - total_pro_time
        overall_vs_pro = f"[red]+{format_ms(overall_vs_diff)}[/]" if overall_vs_diff > 0 else f"[cyan]-{format_ms(abs(overall_vs_diff))}[/]"

        table.add_section()
        table.add_row(
            "[bold white]OVERALL[/]",
            format_ms(total_user_time),
            f"[bold {RANK_COLORS[overall_rank]}]{overall_rank.capitalize()}[/]",
            overall_to_rank_up_str,
            overall_seed_diff,
            format_ms(total_pro_time),
            overall_vs_pro
        )

    return table

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

def write(text):
    try:
        prev_pause = pydirectinput.PAUSE
        pydirectinput.PAUSE = 0.01
        time.sleep(0.05)
        pydirectinput.press(REBIND_TOGGLE_HOTKEY)
        if REBIND_TOGGLE_HOTKEY.isprintable():
            pydirectinput.press('backspace')
        pydirectinput.write(text, interval=0.01)
        pydirectinput.PAUSE = prev_pause
        time.sleep(0.05)
        pydirectinput.press(REBIND_TOGGLE_HOTKEY)
        if REBIND_TOGGLE_HOTKEY.isprintable():
            pydirectinput.press('backspace')
        time.sleep(0.05)
    except:
        pyautogui.write(text, interval=0.01)
        time.sleep(0.05)

def get_loaded_world_name():
    if not os.path.exists(LOG_PATH):
        return "seedscraper"
    with open(LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        for line in reversed(lines):
            if "Attempting event world load at" in line:
                parts = line.split("Attempting event world load at ")
                if len(parts) > 1:
                    return parts[1].strip()
    return "seedscraper"

def wait_for_world_load():
    with open(LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.2)
                continue
            if "logged in with entity id" in line:
                time.sleep(1.0)
                return get_loaded_world_name()

def wait_for_world_exit():
    with open(LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            if "lost connection:" in line or "Stopping singleplayer server" in line:
                time.sleep(1.5)
                return True

try:
    pydirectinput.PAUSE = 0.02
except:
    ...

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
        pydirectinput.press('backspace')
        pydirectinput.keyUp('ctrl')
        write('seedscraper')
        progress.advance(task)
        # Adv. seed
        shift_tab(1)
        if seed:
            pydirectinput.press('enter')
            progress.advance(task)
            tab(4)
            write(seed['overworldSeed'])
            tab(1)
            progress.advance(task)
            write(seed['netherSeed'])
            tab(1)
            progress.advance(task)
            write(seed['theEndSeed'])
            tab(2)
            progress.advance(task)
            pydirectinput.press('enter')
        else:
            progress.update(task, advance=4)
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

def local_splits(world_name):
    igt_path = os.path.join(MINECRAFT_PATH, "saves", world_name, "speedrunigt", "record.json")
    if not os.path.exists(igt_path):
        print(f"[[red bold]ERROR[/]] Speedrunigt not initialized ({igt_path}).")
        return None
    splits = [(0, "overworld")]
    with open(igt_path, "r") as f:
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

if __name__ == "__main__":
    console = Console()

    print("[[blue bold]INFO[/]] To [cyan bold]watch the pro replay[/] of the current seed, go to mcsr ranked -> my replays, the replay should be [cyan bold]first[/] in the list.")
    with open(PLAY_SEEDS_FILE, 'r') as f:
        lines = f.readlines()
    print(f"[[blue bold]INFO[/]] {len(lines)} seeds remaining.")
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
        replay_path = REPLAY_PATH + "/seedscraper_" + str(seed["matchId"]) + ".rrf"
        print("[[green bold]OK[/]] Found seed.")
        if os.path.exists(replay_path):
            os.utime(replay_path, None)
        else:
            print("[[yellow bold]WARN[/]] No replay file for this seed.")
        winner = seed['winner']
        expected_splits = ['overworld', 'nether', 'bastion', 'fortress', 'blind', 'stronghold', 'end', 'finish']
        winner_splits = [s[1] for s in seed['splits'][winner or 0]]
        if winner_splits != expected_splits:
            print(f"[[yellow bold]WARN[/]] Unexpected splits: ", end="")
            for j, s in enumerate(winner_splits):
                if s == 'finish':
                    break
                if j:
                    print(" -> ", end="")
                print(f"[{STYLES[s][0]}]{s}", end="")
            print()
        print(f"[[blue bold]TYPE[/]] [yellow]{seed['type']}")
        print(f"[[blue bold]GAME[/]] ", end="")
        last = len(seed['players']) - 1
        for (j, p) in enumerate(seed['players']):
            if j == winner:
                print(f"[green]{p}[/]", end="")
            else:
                print(f"[red]{p}[/]", end="")
            if j != last:
                print(" vs ", end="")
        print(f", {readable_date}")

        if 'vods' in seed:
            for v in seed['vods']:
                print(f"[[blue bold]VOD[/]] ", end="")
                print(v)

        while True:
            print("[[blue bold]INFO[/]] The script will sleep for 3 seconds then create this world. Make sure to tab into mcsr ranked during this time.")
            print("[[blue bold]INFO[/]] Make sure to be in the [bold cyan]minecraft main menu[/], not the ranked main menu.")
            print("[dim]Press enter to continue, 'p' to use MPK, 'd' to display the seed, 's' to skip this seed.")
            inp = input()
            if inp == "s":
                break

            if inp != "d":
                with console.status("[bold cyan]Creating world...", spinner_style="bold cyan") as status:
                    for j in range(3, 0, -1):
                        status.update(f"Creating world in [bold cyan]{j}[/]...")
                        time.sleep(1)
                create_world(seed, inp == "p")
            if inp == "p":
                print("[[blue bold]INFO[/]] Waiting for world load to use MPK.")
            elif inp == "d":
                print(f"[[blue bold]OVERWORLD[/]] {seed['overworldSeed']}")
                print(f"[[blue bold]NETHER[/]]    {seed['netherSeed']}")
                print("[[blue bold]INFO[/]] Waiting for world load.")

            loaded_world_name = wait_for_world_load()

            if inp == "p":
                pydirectinput.keyDown(LOAD_HOTBAR_BIND)
                pydirectinput.press('1')
                pydirectinput.keyUp(LOAD_HOTBAR_BIND)
            print(f"[[green bold]OK[/]] World loaded: [cyan]{loaded_world_name}[/]")
            try:
                recorder = pyscreenrec.ScreenRecorder()
                recorder.start_recording("game.mp4", 20)
            except:
                ...
            print("[[blue bold]INFO[/]] Recording started. Waiting for world exit.")
            wait_for_world_exit()
            try:
                recorder.stop_recording()
            except:
                ...
            print("[dim]Press enter after playing to see your splits, 'r' to restart the current seed.")
            inp = input()
            if inp == "r":
                continue
            all_splits = []
            for (j, (p, s)) in enumerate(zip(seed['players'], seed['splits'])):
                all_splits.append((p, s, j == winner))

            sp = local_splits(loaded_world_name)
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

                table = generate_splits_table(sp, all_splits[winner or 0][1], seed['type'])
                console.print(table)

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

