"""
NFT launch watch tower - web version.

Runs a background thread that polls X API v2's recent-search endpoint,
and serves a single-page dashboard that receives new matches live over
Server-Sent Events (no page refresh needed).

Usage:
    python app.py
Then open http://localhost:5000 in a browser.
"""
import os
import json
import time
import queue
import threading
from datetime import datetime, timezone

import tweepy
from flask import Flask, Response, render_template, jsonify
from dotenv import load_dotenv

from config import (
    KEYWORDS,
    WATCHLIST,
    FRESH_ACCOUNT_MAX_TWEETS,
    FRESH_ACCOUNT_MAX_FOLLOWERS,
    POLL_INTERVAL_SECONDS,
    POLL_MAX_RESULTS,
    HISTORY_LIMIT,
)

load_dotenv()

BEARER_TOKEN = os.environ["TWITTER_BEARER_TOKEN"]
x_client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

app = Flask(__name__)

lock = threading.Lock()
alert_history = []
seen_tweet_ids = set()
subscribers = []
status = {
    "started_at": datetime.now(timezone.utc).isoformat(),
    "last_poll_at": None,
    "last_error": None,
    "match_count": 0,
}


def is_likely_fresh_account(user: dict) -> bool:
    metrics = user.get("public_metrics", {})
    tweet_count = metrics.get("tweet_count", 10**9)
    followers = metrics.get("followers_count", 10**9)
    return tweet_count <= FRESH_ACCOUNT_MAX_TWEETS and followers <= FRESH_ACCOUNT_MAX_FOLLOWERS


def build_query() -> str:
    keyword_clause = " OR ".join(f'"{k}"' for k in KEYWORDS)
    clause = f"({keyword_clause})"
    if WATCHLIST:
        watch_clause = " OR ".join(f"from:{u}" for u in WATCHLIST)
        clause = f"({clause}) OR ({watch_clause})"
    clause += " -is:retweet -is:reply"
    return clause


def broadcast(alert: dict) -> None:
    with lock:
        alert_history.insert(0, alert)
        del alert_history[HISTORY_LIMIT:]
        status["match_count"] += 1
        for q in subscribers:
            q.put(alert)


def poll_loop():
    query = build_query()
    print(f"[watcher] polling every {POLL_INTERVAL_SECONDS}s with query: {query}")
    while True:
        try:
            resp = x_client.search_recent_tweets(
                query=query,
                max_results=min(max(POLL_MAX_RESULTS, 10), 100),
                tweet_fields=["author_id", "created_at"],
                user_fields=["public_metrics", "created_at"],
                expansions=["author_id"],
            )
            with lock:
                status["last_poll_at"] = datetime.now(timezone.utc).isoformat()
                status["last_error"] = None

            if resp.data:
                users = (
                    {u.id: u.data for u in resp.includes.get("users", [])}
                    if resp.includes
                    else {}
                )
                for tweet in reversed(resp.data):
                    if tweet.id in seen_tweet_ids:
                        continue
                    seen_tweet_ids.add(tweet.id)

                    author = users.get(tweet.author_id, {})
                    username = author.get("username", "unknown")
                    metrics = author.get("public_metrics", {})

                    alert = {
                        "id": str(tweet.id),
                        "username": username,
                        "text": tweet.text,
                        "followers": metrics.get("followers_count", "?"),
                        "tweet_count": metrics.get("tweet_count", "?"),
                        "is_fresh": is_likely_fresh_account(author),
                        "url": f"https://x.com/{username}/status/{tweet.id}",
                        "seen_at": datetime.now(timezone.utc).isoformat(),
                    }
                    broadcast(alert)
        except Exception as e:
            with lock:
                status["last_error"] = str(e)
            print(f"[watcher] error: {e}")
        time.sleep(POLL_INTERVAL_SECONDS)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/history")
def history():
    with lock:
        return jsonify(
            {
                "alerts": alert_history,
                "status": status,
                "config": {
                    "keywords": KEYWORDS,
                    "watchlist": WATCHLIST,
                    "poll_interval": POLL_INTERVAL_SECONDS,
                },
            }
        )


@app.route("/stream")
def stream():
    def gen():
        q = queue.Queue()
        with lock:
            subscribers.append(q)
        try:
            while True:
                alert = q.get()
                yield f"data: {json.dumps(alert)}\n\n"
        finally:
            with lock:
                if q in subscribers:
                    subscribers.remove(q)

    return Response(gen(), mimetype="text/event-stream")


if __name__ == "__main__":
    threading.Thread(target=poll_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=False)
