# --- Scraping config ---
# Path to the minecraft folder of the mcsr ranked instance
MINECRAFT_PATH = r"C:\Users\barte\AppData\Roaming\PrismLauncher\instances\MCSRRanked-Windows-1.16.1\minecraft"

# Path to the file in which ranked seeds will be saved
SEEDS_FILE = "seeds.txt"

# Which seeds to save
SAVE_SEEDS = {
    "Village": True,
    "Buried Treasure": False,
    "Ruined Portal": False,
    "Shipwreck": False,
    "Desert Temple": False
}

# --- Playing config ---
# Path to the minecraft folder of the playing instance
PLAY_MINECRAFT_PATH = r"C:\Users\barte\AppData\Roaming\PrismLauncher\instances\1.16.1\minecraft"

# Path to the file where the seeds are
PLAY_SEEDS_FILE = SEEDS_FILE

# Which seeds to play
PLAY_SEEDS = SAVE_SEEDS

