# mcsr-ranked-seed-scraper

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

To play the resulting seeds, launch mcsr ranked (any resolution) and run `play.py`.

```
python play.py
```
