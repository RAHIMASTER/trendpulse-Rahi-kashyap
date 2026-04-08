# NAME - RAHI KASHYAP 


import requests
import json
import os
import time
from datetime import datetime


CATEGORIES = {
    "technology":    ["ai", "software", "tech", "code", "computer", "data", "cloud", "api", "gpu", "llm"],
    "worldnews":     ["war", "government", "country", "president", "election", "climate", "attack", "global"],
    "sports":        ["nfl", "nba", "fifa", "sport", "game", "team", "player", "league", "championship"],
    "science":       ["research", "study", "space", "physics", "biology", "discovery", "nasa", "genome"],
    "entertainment": ["movie", "film", "music", "netflix", "game", "book", "show", "award", "streaming"],
}

# base urL
HN_BASE = "https://hacker-news.firebaseio.com/v0"

# adding a user-agent header 
HEADERS = {"User-Agent": "TrendPulse/1.0"}

# only want 25 per category, 5 categories = 125 max
MAX_PER_CATEGORY = 25


def get_top_story_ids():
    """Hits the HN topstories endpoint and returns the first 500 IDs."""
    url = f"{HN_BASE}/topstories.json"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        ids = resp.json()
        # only grabbing first 500 as per the task spec
        return ids[:500]
    except requests.RequestException as e:
        print(f"Couldn't fetch top stories list: {e}")
        return []


def get_story_details(story_id):
    """Fetches a single story by its ID. Returns None if anything goes wrong."""
    url = f"{HN_BASE}/item/{story_id}.json"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        
        print(f"  Failed to fetch story {story_id}: {e}")
        return None


def figure_out_category(title):
    """
    Checks a story title against our keyword lists and returns the first
    matching category. Returns None if nothing matches.
    Quick note: if a title matches multiple categories the first one in
    CATEGORIES dict order wins — felt like the simplest approach.
    """
    if not title:
        return None

    lowered = title.lower()
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            
            if kw in lowered:
                return cat
    return None


def collect_stories(story_ids):
    """
    Main collection loop. Goes through all story IDs, tries to assign each
    one a category, and keeps collecting until we hit 25 per category.
    Waits 2 seconds after filling up each category bucket.
    """
    # bucket to hold stories per category
    buckets = {cat: [] for cat in CATEGORIES}

    # track which categories are already full so we can stop early
    full_cats = set()

    for sid in story_ids:
        # if all categories are full we're done, no point continuing
        if len(full_cats) == len(CATEGORIES):
            break

        story = get_story_details(sid)

        # skip if request failed or if it's not a regular story (could be a job post etc.)
        if not story or story.get("type") != "story":
            continue

        title = story.get("title", "")
        cat = figure_out_category(title)

        if not cat:
            # no matching category, skip it
            continue

        if cat in full_cats:
            # already have 25 for this category
            continue

        # pull out only the fields we care about
        record = {
            "post_id":      story.get("id"),
            "title":        title,
            "category":     cat,
            "score":        story.get("score", 0),
            "num_comments": story.get("descendants", 0),  
            "author":       story.get("by", "unknown"),
            "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        buckets[cat].append(record)

        # check if this category just got full
        if len(buckets[cat]) >= MAX_PER_CATEGORY:
            full_cats.add(cat)
            print(f"  [{cat}] reached {MAX_PER_CATEGORY} stories — sleeping 2s...")
            time.sleep(2) 

    return buckets


def save_to_json(all_stories):
    """Puts everything into a flat list and saves to data/trends_YYYYMMDD.json"""
    # create data/ folder if it's not already there
    os.makedirs("data", exist_ok=True)

    today = datetime.now().strftime("%Y%m%d")
    filename = f"data/trends_{today}.json"

    # flatten the buckets into one list
    flat_list = []
    for cat_stories in all_stories.values():
        flat_list.extend(cat_stories)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(flat_list, f, indent=2, ensure_ascii=False)

    return filename, len(flat_list)


def main():
    print("TrendPulse — fetching trending stories from HackerNews")
    print("=" * 55)

    print("\nStep 1: Getting top story IDs...")
    story_ids = get_top_story_ids()

    if not story_ids:
        print("Got nothing back from the API. Check your connection and try again.")
        return

    print(f"Got {len(story_ids)} story IDs to work through.\n")

    print("Step 2: Fetching individual stories and categorising...")
    buckets = collect_stories(story_ids)

    # quick summary of what we got per category
    print("\n--- Category breakdown ---")
    for cat, stories in buckets.items():
        print(f"  {cat:<15} {len(stories)} stories")

    print("\nStep 3: Saving results...")
    filepath, total = save_to_json(buckets)

    print(f"\nCollected {total} stories. Saved to {filepath}")

    # warn if we came up short
    if total < 100:
        print(f"Warning: only got {total} stories, which is below the 100 minimum.")
        print("The API might be returning fewer matching titles right now — try running again.")


if __name__ == "__main__":
    main()
