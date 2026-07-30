import sys
import requests
from beaupy import select, prompt
from rich.console import Console

console = Console()

console.print("[bold yellow]Select Player Mode[/bold yellow]")
player_mode = select(["Specific", "Top 10", "Top 50"])

try:
    leaderboard_data = requests.get("https://api.mcsrranked.com/leaderboard").json()["data"]["users"]
except Exception:
    console.print("[bold red]Failed to fetch leaderboard data.[/bold red]")
    sys.exit(1)

leaderboard_nicknames = [u["nickname"] for u in leaderboard_data]
user_map = {u["nickname"].lower(): (u["nickname"], u["uuid"]) for u in leaderboard_data}

target_users = []
if player_mode == "Specific":
    console.print("[bold yellow]Enter custom or autocompleted nickname (Press Tab to show suggestions):[/bold yellow]")
    autocomplete_fn = lambda val: [name for name in leaderboard_nicknames if name.lower().startswith(val.lower())]
    target_name = prompt("Nickname: ", completion=autocomplete_fn)
    if not target_name:
        console.print("[bold red]No nickname entered.[/bold red]")
        sys.exit(1)
    
    if target_name.lower() in user_map:
        target_users.append(user_map[target_name.lower()])
    else:
        try:
            res = requests.get(f"https://api.mcsrranked.com/users/{target_name}").json()
            if res.get("status") == "success":
                target_users.append((res["data"]["nickname"], res["data"]["uuid"]))
            else:
                console.print(f"[bold red]Player '{target_name}' not found.[/bold red]")
                sys.exit(1)
        except Exception:
            console.print("[bold red]Failed to fetch custom player data.[/bold red]")
            sys.exit(1)
elif player_mode == "Top 10":
    target_users = [(u["nickname"], u["uuid"]) for u in leaderboard_data[:10]]
elif player_mode == "Top 50":
    target_users = [(u["nickname"], u["uuid"]) for u in leaderboard_data[:50]]

console.print("[bold yellow]What do you want to review?[/bold yellow]")
review_type = select(["Overworld", "Bastion", "Fortress"])

struct_type = None
ow_filter = "ANY"
ow_options = ["Any", "Village", "Desert Temple", "Buried Treasure", "Shipwreck", "Ruined Portal"]

if review_type == "Overworld":
    console.print("[bold yellow]Select overworld type[/bold yellow]")
    selected_ow = select(ow_options[1:])
    ow_filter = selected_ow.upper().replace(" ", "_")
    struct_type = ow_filter
elif review_type == "Bastion":
    console.print("[bold yellow]Select bastion type[/bold yellow]")
    struct_type = select(["Treasure", "Bridge", "Housing", "Stables"]).upper()
    console.print("[bold yellow]Select overworld type[/bold yellow]")
    selected_ow = select(ow_options)
    ow_filter = "ANY" if selected_ow == "Any" else selected_ow.upper().replace(" ", "_")
elif review_type == "Fortress":
    console.print("[bold yellow]Select overworld type[/bold yellow]")
    selected_ow = select(ow_options)
    ow_filter = "ANY" if selected_ow == "Any" else selected_ow.upper().replace(" ", "_")

for nickname, uuid in target_users:
    try:
        user_matches = requests.get(f"https://api.mcsrranked.com/users/{nickname}/matches?excludedecay=true").json().get("data", [])
    except Exception:
        continue

    for match_sum in user_matches:
        if not match_sum.get("vod"):
            continue

        try:
            match_details = requests.get(f"https://api.mcsrranked.com/matches/{match_sum['id']}").json().get("data", {})
        except Exception:
            continue

        seed_info = match_details.get("seed", {}) or {}
        
        if ow_filter != "ANY" and seed_info.get("overworld") != ow_filter:
            continue
        if review_type == "Bastion" and seed_info.get("nether") != struct_type:
            continue

        start_time = match_details["date"] - (match_details["result"]["time"] // 1000)

        if review_type in ("Bastion", "Fortress"):
            event_type = "nether.find_bastion" if review_type == "Bastion" else "nether.find_fortress"
            found_event = False
            for event in reversed(match_details.get("timelines", [])):
                if event["type"] == event_type and event.get("uuid") == uuid:
                    start_time += event["time"] // 1000
                    found_event = True
                    break
            if not found_event:
                continue

        for vod in match_details.get("vod", []):
            if vod.get("uuid") == uuid:
                ow_type = seed_info.get("overworld")
                print(f"{nickname} {ow_type} {vod['url']}?t={start_time - vod['startsAt']}s")
