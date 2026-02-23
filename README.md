# mcsr-ranked-seed-scraper

> [!WARNING]  
> This doesn't quite work as intended because mcsr ranked adds a lot of artificial structures to their worlds instead of actually finding good seeds.

A python bot which uses the mcsr ranked client to download replays from the leaderboard and extract the seeds.

## Setup

Create a virtual environment and install dependencies

```
python -m venv venv
.\venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Usage

Make sure the virtual environment is active.

```
.\venv\Scripts\activate.bat
```

To scrape, launch mcsr ranked at 400x400 resolution and run `scrape.py`.

```
python scrape.py
```

To play the resulting seeds, launch a 1.16.1 instance and run `play.py`.

```
python play.py
```
