import os
import glob
import json
import shutil
from rich import print
from config import MINECRAFT_PATH, SEEDS_FILE

replay_dir = os.path.join(MINECRAFT_PATH, "mcsrranked", "replay")
saves_dir = os.path.join(MINECRAFT_PATH, "saves")
pattern = os.path.join(replay_dir, "seed_scraper_*.rrf")

print("[dim]Press enter to remove orphaned replays and seeds, 'c' to clear [cyan bold]all[/] replays and seeds, 'w' to clear junk worlds.")
inp = input()

if inp == "":
    replay_files = glob.glob(pattern)
    replay_ids = {os.path.basename(r).replace("seed_scraper_", "").replace(".rrf", "") for r in replay_files}
    valid_seed_ids = set()
    kept_seeds =[]
    if os.path.exists(SEEDS_FILE):
        with open(SEEDS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    match_id = str(json.loads(line).get("matchId"))
                    valid_seed_ids.add(match_id)
                    if match_id in replay_ids:
                        kept_seeds.append(line)
                    else:
                        print(f"[[red bold]SEED[/]] {match_id}")
        with open(SEEDS_FILE, 'w', encoding='utf-8') as f:
            f.writelines(kept_seeds)
    for replay in replay_files:
        match_id = os.path.basename(replay).replace("seed_scraper_", "").replace(".rrf", "")
        if match_id not in valid_seed_ids:
            os.remove(replay)
            print(f"[[red bold]REPLAY[/]] {os.path.basename(replay)}")
elif inp == "c":
    for replay in glob.glob(pattern):
        os.remove(replay)
        print(f"[[red bold]REPLAY[/]] {os.path.basename(replay)}")
    open(SEEDS_FILE, 'w').close()
    print(f"[[red bold]ALL SEEDS[/]] {os.path.basename(SEEDS_FILE)}")
elif inp == "w":
    junk_patterns =[
        os.path.join(saves_dir, "New World"),
        os.path.join(saves_dir, "New World (*)"),
        os.path.join(saves_dir, "mcsrranked #*")
    ]
    for pat in junk_patterns:
        for world_path in glob.glob(pat):
            if os.path.isdir(world_path):
                shutil.rmtree(world_path)
                print(f"[[red bold]WORLD[/]] {os.path.basename(world_path)}")
