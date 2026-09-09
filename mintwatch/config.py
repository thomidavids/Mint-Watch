"""
Tune everything here. No code changes needed elsewhere for basic use.
"""

# Phrases that suggest an NFT mint/launch is happening or imminent.
# Keep these fairly specific - broad words like "NFT" alone will flood you
# with noise.
KEYWORDS = [
    "minting now",
    "mint is live",
    "mint live",
    "stealth mint",
    "wl mint",
    "public mint",
    "free mint",
    "minting soon",
    "just launched",
    "collection is live",
    "genesis mint",
]

# X usernames (no @) you always want an instant alert for, regardless of
# keyword matching. Good for founders/projects you already know about.
WATCHLIST = [
    # "example_project_founder",
]

# Heuristic thresholds for flagging an author as "likely a brand new
# project account" (i.e. this could be their first real post).
FRESH_ACCOUNT_MAX_TWEETS = 25
FRESH_ACCOUNT_MAX_FOLLOWERS = 300

# How often the background watcher polls X's recent-search endpoint.
POLL_INTERVAL_SECONDS = 15

# X's recent search endpoint only covers the last 7 days, and results are
# capped; this governs how many results we pull per poll.
POLL_MAX_RESULTS = 25

# How many past matches to keep in memory / show on page load.
HISTORY_LIMIT = 200
