import time
import pyautogui
import json
import os
from zipfile import ZipFile
from rich import print
from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn, MofNCompleteColumn
from config import MINECRAFT_PATH, SEEDS_FILE, SAVE_SEEDS

REPLAY_PATH = MINECRAFT_PATH + "/mcsrranked/replay/seed_scraper.rrf"
if os.path.exists(REPLAY_PATH):
    os.remove(REPLAY_PATH)

class TempLoc:
    def __init__(self, left, top):
        self.top = top
        self.left = left
print("[[blue bold]INFO[/]] Set your mcsr ranked instance resolution to [cyan bold]400x400[/] in your launcher and launch it.")
print("[dim]Press enter to continue")
input()
try:
    loc = pyautogui.locateOnScreen('title.png')
except:
    print("[[red bold]ERROR[/]] Couldn't find an mcsr ranked window on the screen")
    exit()
    # loc = TempLoc(119, 674)
print(f"[[green bold]OK[/]] Found mcsr ranked at ({loc.left}, {loc.top})")
print("[[blue bold]INFO[/]] Don't move the mcsr window from here")
print("[[blue bold]INFO[/]] To stop scraping, try to move the cursor into a corner")

print("[dim]Press enter to start scraping")
input()

pyautogui.PAUSE = 0.1
def click(x, y):
    pyautogui.moveTo(x, y)
    time.sleep(0.01)
    pyautogui.click(x, y)

def wait_for_pixel(x, y, expected_red, bad_red = None, debug = False):
    if debug:
        print(f"Waiting for pixel ({expected_red})")
    last_pix = None
    for i in range(50):
        pix = pyautogui.pixel(x, y)
        if debug and pix != last_pix:
            print(f"Change {last_pix} -> {pix}")
            last_pix = pix
        if pix[0] == expected_red:
            return
        if pix[0] == bad_red:
            raise Exception("Bad pixel")
        time.sleep(0.2)
    raise Exception("Timeout")


def get_seed_type(pix):
    match pix[0]:
        case 124:
            return "Village"
        case 216:
            return "Desert Temple"
        case 110:
            return "Shipwreck"
        case 252:
            return "Buried Treasure"
        case 4:
            return "Ruined Portal"
    return None

def save_seed(seed_type, meta):
    if seed_type is None:
        return
    with open(SEEDS_FILE, "a") as f:
        info = {
                "type": seed_type,
                "overworldSeed": meta["overworldSeed"],
                "netherSeed": meta["netherSeed"],
                "theEndSeed": meta["theEndSeed"],
                "date": meta["date"],
                "players": [player["nickname"] for player in meta["players"]]
                }
        f.write(json.dumps(info))
        f.write("\n")

def scrape_page(loc, on_seed):
    im = pyautogui.screenshot()
    y = loc.top + 15 - 11
    for i in range(20):
        y += 11
        # Look at the seed image of a match
        # If player doesn't complete a run, the seed image will be offset
        pix = im.getpixel((loc.left + 117, y + 4))
        seed = get_seed_type(pix)
        if seed is None:
            pix = im.getpixel((loc.left + 101, y + 4))
            seed = get_seed_type(pix)
        if seed is None:
            continue
        if not SAVE_SEEDS[seed]:
            continue

        # Click on the match
        click(loc.left, y)

        # Wait for match to load and download replay
        try:
            wait_for_pixel(loc.left + 181, loc.top + 326, 111, bad_red = 44)
        except Exception as e:
            click(loc.left + 58, loc.top + 350)
            raise e
        click(loc.left + 181, loc.top + 326)
        # In the replay saving menu, name the replay and press download 
        pyautogui.write('seed_scraper')
        click(loc.left + 81, loc.top + 186)

        # Wait for replay to download and exit out of the match
        wait_for_pixel(loc.left + 58, loc.top + 350, 111)
        click(loc.left + 58, loc.top + 350)

        # Get the seed from the replay
        with ZipFile(REPLAY_PATH, 'r') as z:
            if 'meta.json' in z.namelist():
                with z.open('meta.json') as f:
                    meta = json.load(f)
                    save_seed(seed, meta)
        os.remove(REPLAY_PATH)

        on_seed()

        # Redo screenshot since we technically updated the match list
        im = pyautogui.screenshot()


# Leaderboard
click(loc.left + 252, loc.top + 307)
# Elo Leaderboard
click(loc.left + 31, loc.top + 126)
wait_for_pixel(loc.left + 208, loc.top + 27, 192)

with Progress(
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    MofNCompleteColumn(),
    TimeRemainingColumn(),
) as progress:
    seeds_task = progress.add_task("[green]Seeds", total=None)
    players_task = progress.add_task("[red]Players", total=150)
    scrolls = [(15, 29), (20, 29), (23, 28), (15, 29), (15, 29), (271, 6)]
    for (start_y, num_players) in scrolls:
        y = loc.top + start_y
        for i in range(num_players):
            # Player
            click(loc.left, y)
            wait_for_pixel(loc.left - 109, loc.top + 357, 2)
            # Matches
            click(loc.left - 89, loc.top + 66)
            wait_for_pixel(loc.left + 127, loc.top + 351, 111)
            try:
                scrape_page(loc, lambda: progress.advance(seeds_task))
            except:
                pass
            # Exit matches
            click(loc.left + 81, loc.top + 352)
            # Exit player
            click(loc.left - 89, loc.top + 356)
            y += 11
            progress.advance(players_task)
        pyautogui.scroll(-23, x = loc.left, y = loc.top + 30)

