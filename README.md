Mint Watch — web version
Same watcher as before, now a live dashboard in your browser instead of a Telegram bot. Leave the tab open (or a browser window on a spare monitor) and matches stream in as they're found, with optional desktop notifications.

What it does
Polls X's recent-search endpoint every 15 seconds for NFT-launch language ("mint is live", "stealth mint", "wl mint", etc. — edit the list in config.py), scores each author by follower count / tweet count to flag likely brand-new project accounts, and pushes matches to the page instantly over Server-Sent Events (no manual refresh).

Same honest caveat as before: no API can confirm "this is literally this account's first tweet ever." The amber "likely first post" badge is a heuristic (low followers + low tweet count), not a guarantee.

Getting your X API bearer token (needed either way)
developer.x.com → create a project/app → Keys and Tokens → generate a Bearer Token. Recent search works on lower tiers than the full filtered stream, but confirm current tier/pricing on X's site since it changes.

Using the dashboard
Click "Enable desktop notifications" once, to get OS-level pop-ups even when the tab isn't focused.
The sidebar shows what keywords are being watched and when the last check ran.
Amber-railed rows = likely first post from a fresh account. Blue-railed rows = keyword match from an account that doesn't look brand-new.
Click "view on X →" on any row to jump straight to the tweet.
Getting a real, public URL (no coding required)
This folder is pre-configured to deploy on Render's free tier with almost no setup. You need two free accounts: GitHub (to hold the code) and Render (to run it).

Create a GitHub account if you don't have one, then create a new repository and use the "Add file → Upload files" button to drag this entire folder in. Commit it.
Create a Render account at render.com and sign in with GitHub.
Click New + → Blueprint, pick the repo you just created. Render reads render.yaml in this folder and configures itself automatically.
When it asks for TWITTER_BEARER_TOKEN, paste in your X API bearer token (never commit this to GitHub directly).
Click Deploy. After a couple of minutes you'll get a live URL like https://mint-watch.onrender.com — that's your website, open it from any device.
Notes on the free tier: it spins down after 15 minutes of no traffic and takes ~30-60s to wake back up on the next visit, and the background polling loop pauses while it's asleep. Fine for checking in periodically; if you want it watching 24/7 without gaps, upgrade to Render's cheapest paid instance type later — no code changes needed.

Running it on your own computer instead
bash
pip install -r requirements.txt
cp .env.example .env
# paste your X API bearer token into .env
python app.py
Then open http://localhost:5000. This only runs while your computer is on and the terminal window is open.

Tuning
Same config.py knobs as the bot version: KEYWORDS, WATCHLIST, FRESH_ACCOUNT_MAX_TWEETS, FRESH_ACCOUNT_MAX_FOLLOWERS, POLL_INTERVAL_SECONDS, POLL_MAX_RESULTS.
