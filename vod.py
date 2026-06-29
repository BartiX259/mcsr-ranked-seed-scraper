import requests
from beaupy import select
from rich.console import Console

console = Console()

console.print("[bold yellow]What do you want to review?[/bold yellow]")
answer = select(["Overworld", "Bastion", "Fortress"])

match answer:
    case "Bastion":
        console.print("[bold yellow]Select bastion type[/bold yellow]")
        bastion = select(["Treasure", "Bridge", "Housing", "Stables"])
        users = [u["nickname"] for u in requests.get("https://api.mcsrranked.com/leaderboard").json()["data"]["users"]]
        for u in users[:10]:
            user_matches = requests.get(f"https://api.mcsrranked.com/users/{u}/matches?excludedecay=true").json()["data"]
            for match in user_matches:
                if match["seed"]["nether"] != bastion.upper():
                    continue
                if not match["vod"]:
                    continue
                ow = match["seed"]["overworld"]
                match = requests.get(f"https://api.mcsrranked.com/matches/{match['id']}").json()["data"]
                start_time = (match["date"] - match["result"]["time"] // 1000)
                for event in reversed(match["timelines"]):
                    if event["type"] == "nether.find_bastion":
                        start_time += event["time"] // 1000
                        break
                vods = [f"{u} {ow} {vod['url']}?t={(start_time - vod['startsAt'])}s" for vod in match["vod"]]
                for vod in vods:
                    print(vod)
