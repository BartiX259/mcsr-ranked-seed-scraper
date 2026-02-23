# mcsr-ranked-seed-scraper

A python bot which uses the MCSR Ranked client to download replays from the leaderboard, extract the seeds and instantly generate them for you to practice.

## Prerequisites

1. Python
2. Minecraft 1.16.1 with the MCSR Ranked mod installed.

## Setup

1. Clone the repository.
2. Create and activate a virtual environment, then install dependencies:

```
python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

3. Edit `config.py` and modify the parameters, most importantly set `MINECRAFT_PATH` to your MCSR Ranked minecraft folder.

## Usage

Make sure the virtual environment is active:

```
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### Scraping Seeds

The scraper uses hardcoded pixel offsets and requires a specific window size to read and navigate the UI.

1. Set the MCSR Ranked instance resolution to exactly **400x400** in your minecraft launcher.
2. Launch MCSR Ranked.
3. Run the script:
   ```bash
   python scrape.py
   ```
4. Follow the terminal prompts. Do not move the Minecraft window or your cursor once the scraping begins. 

### Playing Seeds

The player script parses `seeds.txt` and uses keyboard automation to navigate the standard Minecraft world creation menus and input the Overworld, Nether, and End seeds.

1. Launch your MCSR Ranked instance (any resolution is fine). 
2. Go to the **standard Minecraft main menu** (not the Ranked main menu).
3. Run the script:
   ```bash
   python play.py
   ```
