import json
import os
import urllib.request
from pathlib import Path

ADDRESS = "NULL_SMP_03.aternos.me:33913"
WEBHOOK = os.environ["DISCORD_WEBHOOK"]
STATE_FILE = Path("last_status.json")

def get_status():
    url = f"https://api.mcsrvstat.us/3/{ADDRESS}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "AternosSMPNotifier/1.0"}
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.loads(response.read().decode("utf-8"))

    if not isinstance(data.get("online"), bool):
        raise ValueError("Unknown server status")

    return data["online"]

def send_message(online):
    if online:
        message = (
            "🟢 **SMP IS NOW ONLINE!**\n"
            "Join the server and start playing!\n"
            f"IP: `{ADDRESS}`"
        )
    else:
        message = "🔴 **SMP IS NOW OFFLINE!**"

    payload = json.dumps({"content": message}).encode("utf-8")
    request = urllib.request.Request(
        WEBHOOK,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        if response.status not in (200, 204):
            raise RuntimeError("Discord notification failed")

current = get_status()
previous = None

if STATE_FILE.exists():
    try:
        previous = json.loads(
            STATE_FILE.read_text(encoding="utf-8")
        ).get("online")
    except (ValueError, OSError):
        previous = None

if previous is None or current != previous:
    send_message(current)

STATE_FILE.write_text(
    json.dumps({"online": current}),
    encoding="utf-8"
)

print("Server status:", "ONLINE" if current else "OFFLINE")
