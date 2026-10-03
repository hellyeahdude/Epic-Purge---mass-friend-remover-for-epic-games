import base64
import colorsys
import os
import re
import sys
import time

import requests

try:
    import pyfiglet
except ImportError:
    pyfiglet = None

BANNER_TEXT = "EPIC PURGE"   
TAGLINE = "bulk friend remover for epic games"
CREDIT = "made by Gloomy-Ninja2693 & hellyeahdude"
DELAY = 0.5                 

CLIENT_ID = "34a02cf8f4414e29b15921876da36f9a"
CLIENT_SECRET = "daafbccc737745039dffe53d94fc76cf"
ACCOUNT = "https://account-public-service-prod.ol.epicgames.com/account/api"
FRIENDS = "https://friends-public-service-prod.ol.epicgames.com/friends/api/v1"


def paint(text, r, g, b):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


def rainbow(text, shift=0.0):
    out = ""
    for i, ch in enumerate(text):
        if ch == " ":
            out += ch
            continue
        r, g, b = colorsys.hsv_to_rgb((i / 45 + shift) % 1, 0.75, 1)
        out += paint(ch, int(r * 255), int(g * 255), int(b * 255))
    return out


def say(msg, color=(220, 220, 220)):
    print(paint(msg, *color))


def die(msg):
    say(msg, (255, 90, 90))
    sys.exit()


def big_text(text):
    if pyfiglet:
        for font in ("ansi_shadow", "standard"):
            try:
                art = pyfiglet.figlet_format(text, font=font, width=110)
                return [l.rstrip() for l in art.split("\n") if l.strip()]
            except Exception:
                continue
    return [" ".join(text.upper())]


def banner():
    os.system("cls" if os.name == "nt" else "clear")
    print()
    for n, line in enumerate(big_text(BANNER_TEXT)):
        print("  " + rainbow(line, n * 0.06))
    print()
    say("  " + TAGLINE, (180, 180, 180))
    print("  " + rainbow(CREDIT, 0.3))
    print()


def login(code):
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    r = requests.post(
        f"{ACCOUNT}/oauth/token",
        headers={"Authorization": "basic " + auth},
        data={"grant_type": "authorization_code", "code": code, "token_type": "eg1"},
        timeout=30,
    )
    if r.status_code != 200:
        die(f"login failed: {r.text}\n(the code only works once, get a new one)")
    j = r.json()
    return j["access_token"], j["account_id"], j.get("displayName", "?")


def get_friends(token, me):
    r = requests.get(f"{FRIENDS}/{me}/summary",
                     headers={"Authorization": "bearer " + token}, timeout=30)
    if r.status_code != 200:
        die(f"couldn't get friends list: {r.text}")
    return [f["accountId"] for f in r.json().get("friends", [])]


def get_names(token, ids):
    names = {}
    for i in range(0, len(ids), 100):
        r = requests.get(f"{ACCOUNT}/public/account",
                         headers={"Authorization": "bearer " + token},
                         params=[("accountId", x) for x in ids[i:i + 100]], timeout=30)
        if r.status_code != 200:
            die(f"couldn't look up names: {r.text}")
        for a in r.json():
            names[a["id"]] = a.get("displayName") or "(no display name)"
    for x in ids:
        names.setdefault(x, "(unknown " + x[:6] + ")")
    return names


def remove(token, me, friend):
    while True:
        r = requests.delete(f"{FRIENDS}/{me}/friends/{friend}",
                            headers={"Authorization": "bearer " + token}, timeout=30)
        if r.status_code in (200, 204):
            return True
        if r.status_code == 429:
            say("  rate limited, waiting 30s", (255, 200, 80))
            time.sleep(30)
            continue
        say(f"  failed: {r.status_code} {r.text[:150]}", (255, 90, 90))
        return False


try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

banner()
say("1. log in to epicgames.com, then open this link in the same browser:")
say(f"   https://www.epicgames.com/id/api/redirect?clientId={CLIENT_ID}&responseType=code",
    (110, 200, 255))
say("2. paste the page text (or just the authorizationCode) below.\n")

raw = input("code: ").strip()
m = re.search(r'"authorizationCode"\s*:\s*"([^"]+)"', raw)
code = m.group(1) if m else raw.strip('"')
if "null" in raw and not m:
    die("authorizationCode was null, you weren't logged in. Log in and try the link again.")

token, me, my_name = login(code)
say("\nlogged in as " + my_name, (120, 255, 150))

ids = get_friends(token, me)
if not ids:
    die("no friends found, nothing to do.")
say(f"{len(ids)} friends, getting names...")
names = get_names(token, ids)
lookup = {}
for fid, n in names.items():
    lookup.setdefault(n.lower(), []).append(fid)

keep_input = input("\nwho do you want to KEEP? (names separated by commas): ")
keep = set()
bad = False
for n in [x.strip() for x in keep_input.split(",") if x.strip()]:
    found = lookup.get(n.lower(), [])
    if len(found) == 1:
        keep.add(found[0])
    else:
        say("  can't match: " + n, (255, 200, 80))
        bad = True
if bad or not keep:
    die("stopping, nobody was removed.")

targets = [f for f in ids if f not in keep]
say("\nkeeping: " + ", ".join(names[k] for k in keep), (120, 255, 150))
say(f"removing {len(targets)} friends", (255, 200, 80))
if input("show the full list of who gets removed? (y/n): ").lower().startswith("y"):
    for f in targets:
        print("  ", names[f])
if input("type REMOVE to start: ").strip() != "REMOVE":
    die("cancelled, nobody was removed.")

print()
count = 0
for i, fid in enumerate(targets, 1):
    if fid in keep:
        continue
    if remove(token, me, fid):
        count += 1
        say(f"[{i}/{len(targets)}] removed {names[fid]}", (150, 150, 150))
    time.sleep(DELAY)

print()
say(f"done, removed {count} friends", (120, 255, 150))
print(rainbow(CREDIT, 0.3))
