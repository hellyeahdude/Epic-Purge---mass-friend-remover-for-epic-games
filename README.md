<div align="center">

![Epic Purge banner](images/banner.png)

**Remove all your Epic Games friends in a few minutes, and keep the ones you want.**

![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)
![License MIT](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

</div>

---

Epic has no "remove all friends" button. If you have a few hundred people on your list, the only way to clean it up is to open each profile and unfriend them one by one. This script does that for you.

You type the display names of the people you want to keep (as many as you like), and it removes everybody else.

## Read this first

- **This is unofficial.** It talks to the same web API the Epic launcher uses. It is not made by or connected to Epic Games, and Epic can change or block this at any time. Using automation on your account may go against Epic's terms, so use it at your own risk.
- **Removing friends can't be undone.** If you remove someone by mistake you have to add them again.
- **The login code is sensitive.** It gives full access to your Epic account. Only paste it into this script on your own computer. Never post it anywhere or send it to anyone, and don't trust anyone who asks for it.
- **Read the code.** You're about to run a script that handles your account login. It's one short file ([`epic_purge.py`](epic_purge.py)) and it only talks to Epic's servers. Nothing is saved to disk.

## What it does

- Lets you pick one or many friends to keep
- Stops without removing anyone if a name you typed doesn't match one of your friends
- Shows you who's kept and how many will be removed, and only starts after you type `REMOVE`
- Pauses between removals and automatically waits if Epic says to slow down
- Open source and private: nothing is saved, collected or sent anywhere except Epic's own servers (see [Privacy](#privacy))
- Big rainbow banner in the terminal, because why not (and you can change the text, see [Customize](#customize))

## What you need

- Python 3.8 or newer ([python.org/downloads](https://www.python.org/downloads/)). On Windows, tick **Add Python to PATH** in the installer.
- Your Epic Games account login

## Setup

Download or clone this repo, open Command Prompt (or a terminal) in the folder, and install the two libraries:

```
pip install -r requirements.txt
```

Then start the script:

```
python epic_purge.py
```

![Install and run](images/04-install-and-run.png)

On macOS or Linux use `python3` instead of `python`.

## Step by step

### 1. Log in to Epic in your browser

When the script starts it prints a link. Before you open it, make sure you're logged in to epicgames.com in your browser. A private/incognito window works well. If you get a sign-in page, log in like normal, including your 2FA code if it asks.

### 2. Open the link and copy the code

Open the link the script printed. You'll see a short block of text with your login code in it. You can copy either just the code, or the whole page (Ctrl+A, then Ctrl+C). The script finds the code by itself.

![Copy the code](images/02-copy-code.png)

If it says `"authorizationCode":null` instead, you weren't logged in. Log in at epicgames.com and open the link again.

![null means not logged in](images/03-null-means-not-logged-in.png)

The code only works once and runs out after a few minutes, so grab it right before you paste it.

### 3. Paste it into the script

Paste it at the `code:` prompt (in Command Prompt, right-click to paste) and press Enter. It logs in and loads your friends list.

![Paste the code](images/05-paste-code.png)

### 4. Type who to keep

Type the display names of the friends you want to keep, separated by commas:

```
BestFriend, Cousin_Mike
```

Capital letters don't matter, but spelling does. If a name can't be matched, or two friends have the same name, the script stops and removes nobody.

Check the `keeping:` line carefully. If it isn't right, just type anything other than `REMOVE` and nothing happens.

![Choose who to keep](images/06-choose-who-to-keep.png)

### 5. Let it run

It removes friends one at a time with a short pause between each, and prints a counter as it goes. If you see "rate limited, waiting 30s" that's normal, it carries on by itself. You can stop it any time with Ctrl+C.

![Removing](images/07-removing.png)

For reference, about 300 friends takes a few minutes (approx 7 minutes) at the default speed.

## Troubleshooting

| Problem | What to do |
|---|---|
| `python` is not recognized | Reinstall Python with **Add Python to PATH** ticked, or try `py epic_purge.py` |
| `No module named requests` | Run `pip install -r requirements.txt` first |
| Login failed / code not found | The code works once and expires fast. Get a new one |
| `authorizationCode` is `null` | You weren't logged in. Log in at epicgames.com, open the link again |
| `can't match: <name>` | Check the spelling against your friends list. If two friends share a display name the script can't tell which one you mean |
| Weird symbols like `←[38;2;...` instead of colors | Your console doesn't support colors. Use Windows Terminal, or a recent Windows 10/11 Command Prompt |
| Lots of "rate limited" messages | Raise `DELAY` to `1.0` and run it again |

## FAQ

**Does it log me out of anything?**
No. It only holds a temporary token in memory while it runs. Nothing is written to disk, and your launcher and browser sessions are untouched. To be thorough, log out of epicgames.com in the browser you used for the code and close that window.

**Can I keep more than one friend?**
Yes. Separate the names with commas.

**Can I undo it?**
No, so double-check the `keeping:` line before you type `REMOVE`.

**Why does it ask me to open a link and copy a code?**
The script needs a login token for your account. Epic gives you one through that link once you're logged in. The script never sees your password.

**Does it work on Mac or Linux?**
It should, since it's plain Python. Use `python3`. The colors need a terminal that supports them (most do).

## How it works

For people who want to know what's happening when the script runs. All calls go to Epic's own servers.

1. Exchanges the one-time code for a token (`POST /account/api/oauth/token`)
2. Gets your friends list (`GET /friends/api/v1/{accountId}/summary`)
3. Looks up display names for those accounts, 100 at a time (`GET /account/api/public/account`)
4. Removes each friend that isn't on your keep list (`DELETE /friends/api/v1/{accountId}/friends/{friendId}`)

These are undocumented endpoints, which is why this can break if Epic changes them.

## Privacy

Your privacy matters, so here's exactly what this does with your data:

- **It's open source.** The whole thing is one short file, [`epic_purge.py`](epic_purge.py). Read every line before you run it if you dont trust me.
- **Nothing is saved.** No files, logs, or config are written to your computer. Your login code and token only exist in memory while the script runs and are gone when you close the window.
- **Nothing is collected.** There's no analytics, no tracking, and no server of mine. I never see your code, your friends list, or anything else.
- **It only talks to Epic.** The only network requests go to Epic's own servers (`epicgames.com`), listed in [How it works](#how-it-works).
- **It never sees your password.** You log in on Epic's own website, and the script only gets a one-time code.

Don't just take my word for it: the code is right there, and anyone can check it.

## Credit

Made by **Gloomy-Ninja2693** AKA **hellyeahdude**

If this saved you an afternoon of clicking, a star on the repo is appreciated.

## License

MIT, see [LICENSE](LICENSE).

*Not affiliated with or endorsed by Epic Games. "Epic Games" is a trademark of its owner.*
