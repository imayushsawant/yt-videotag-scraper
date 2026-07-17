"""
YouTube Video ID Word Hunter -- Reverse Scanner

Instead of checking if words are video IDs (forward scanning),
this module searches YouTube for videos and checks if their IDs
happen to be meaningful English words or phrases.

This is MUCH more likely to find hits because we're sampling from
actual video IDs and checking for word patterns.

Uses the YouTube Data API v3 (requires an API key) OR
falls back to scraping search results.
"""

import re
import json
import random
import string
import requests
import time
from pathlib import Path
from typing import Optional

VALID_CHARS = set(string.ascii_letters + string.digits + "-_")
DATA_DIR = Path(__file__).parent / "data"
RESULTS_FILE = DATA_DIR / "results.json"
REVERSE_LOG = DATA_DIR / "reverse_checked_ids.json"


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def is_word_like(video_id: str) -> Optional[dict]:
    """
    Check if a YouTube video ID looks like a meaningful English word or phrase.
    
    Returns a dict with analysis if meaningful, None otherwise.
    """
    # Must be exactly 11 characters
    if len(video_id) != 11:
        return None
    
    # Only consider IDs that are purely alphabetic (a-zA-Z)
    # since words don't contain digits, hyphens, or underscores
    if not video_id.isalpha():
        return None
    
    # Load word list for checking
    from wordgen import _get_common_words
    common = set(w.lower() for w in _get_common_words())
    
    lower_id = video_id.lower()
    
    # Check 1: Is it a single 11-letter word?
    if lower_id in common:
        return {
            "type": "single_word",
            "words": [lower_id],
            "readable": lower_id,
        }
    
    # Check 2: Can it be split into 2+ meaningful words?
    splits = _find_word_splits(lower_id, common)
    if splits:
        best = max(splits, key=lambda s: min(len(w) for w in s))  # prefer longer words
        return {
            "type": f"{len(best)}_word_combo",
            "words": best,
            "readable": " ".join(best),
        }
    
    return None


def _find_word_splits(text: str, word_set: set, min_word_len: int = 2) -> list[list[str]]:
    """
    Find all ways to split text into valid English words.
    Uses dynamic programming.
    """
    n = len(text)
    # dp[i] = list of ways to split text[:i] into words
    dp: list[list[list[str]]] = [[] for _ in range(n + 1)]
    dp[0] = [[]]  # empty split for empty string
    
    for i in range(1, n + 1):
        for j in range(max(0, i - 10), i):  # words up to 10 chars
            word = text[j:i]
            if len(word) >= min_word_len and word in word_set:
                for prev_split in dp[j]:
                    dp[i].append(prev_split + [word])
    
    # Filter: require all parts to be real words, and at least 2 words
    # or 1 word if it's the full string
    results = []
    for split in dp[n]:
        if len(split) >= 2 and all(len(w) >= min_word_len for w in split):
            results.append(split)
        elif len(split) == 1 and split[0] == text:
            results.append(split)
    
    return results


def extract_video_ids_from_html(html: str) -> list[str]:
    """Extract YouTube video IDs from HTML content."""
    # Pattern matches YouTube video IDs in various URL formats
    patterns = [
        r'"videoId"\s*:\s*"([a-zA-Z0-9_-]{11})"',
        r'/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'"url"\s*:\s*"/watch\?v=([a-zA-Z0-9_-]{11})"',
    ]
    
    ids = set()
    for pattern in patterns:
        for match in re.finditer(pattern, html):
            ids.add(match.group(1))
    
    return list(ids)


def search_youtube_for_ids(query: str, timeout: float = 10.0) -> list[str]:
    """
    Search YouTube and extract video IDs from search results.
    No API key needed - just scrapes the search page.
    """
    try:
        url = "https://www.youtube.com/results"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        resp = requests.get(
            url,
            params={"search_query": query},
            headers=headers,
            timeout=timeout,
        )
        resp.raise_for_status()
        return extract_video_ids_from_html(resp.text)
    except Exception as e:
        return []


# Search terms to find lots of diverse video IDs
SEARCH_TERMS = [
    # Broad topics
    "music video", "tutorial", "how to", "review", "unboxing",
    "cooking recipe", "travel vlog", "gaming", "news today",
    "funny animals", "cute cats", "dog tricks", "nature documentary",
    "science experiment", "math tutorial", "history documentary",
    "workout routine", "yoga for beginners", "meditation guide",
    "painting tutorial", "photography tips", "coding tutorial",
    "python programming", "javascript react", "machine learning",
    "motivational speech", "ted talk", "comedy stand up",
    "movie trailer", "book review", "podcast highlights",
    "car review", "phone review", "laptop comparison",
    "football highlights", "basketball", "cricket highlights",
    "chess game", "speedrun", "minecraft build",
    "fortnite gameplay", "among us", "roblox",
    "asmr", "relaxing music", "lofi hip hop",
    "indie music", "rock music", "jazz piano",
    "classical music", "opera singing", "beatboxing",
    "street food", "restaurant review", "baking cake",
    "home renovation", "garden tour", "room makeover",
    "fashion haul", "makeup tutorial", "skincare routine",
    "life advice", "productivity tips", "morning routine",
    "night routine", "study tips", "exam preparation",
    "space exploration", "black hole", "quantum physics",
    "dinosaurs", "ocean exploration", "volcano eruption",
    "earthquake footage", "storm chasing", "northern lights",
    "sunrise timelapse", "sunset beautiful", "mountain climbing",
    "surfing waves", "skateboarding tricks", "parkour",
    "magic tricks revealed", "card tricks", "illusion",
    "origami tutorial", "drawing anime", "digital art",
    "3d printing", "electronics project", "arduino robot",
    "drone footage", "gopro adventure", "dashcam compilation",
    "wedding ceremony", "graduation speech", "birthday surprise",
    "prank video", "challenge accepted", "try not to laugh",
    "baby first steps", "toddler funny", "kids react",
    "elderly wisdom", "veteran stories", "rescue mission",
    "random video", "first video ever", "old youtube",
    "viral video", "trending now", "most viewed",
    "satisfying video", "oddly satisfying", "compilation",
    "top 10", "worst ever", "best ever", "world record",
    # Non-English to get diverse IDs
    "hindi song", "korean drama", "japanese anime",
    "spanish music", "french cooking", "german engineering",
    "arabic calligraphy", "chinese martial arts", "thai food",
    "bollywood dance", "k-pop", "reggaeton",
    # Random / diverse
    "how things are made", "factory tour", "behind the scenes",
    "day in my life", "what i eat", "apartment tour",
    "college life", "road trip usa", "backpacking europe",
    "island vacation", "camping adventure", "fishing trip",
]


def load_reverse_checked() -> set[str]:
    """Load previously checked IDs from reverse scanning."""
    _ensure_data_dir()
    if REVERSE_LOG.exists():
        try:
            with open(REVERSE_LOG, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except (json.JSONDecodeError, IOError):
            return set()
    return set()


def save_reverse_checked(ids: set[str]):
    """Save checked IDs."""
    _ensure_data_dir()
    with open(REVERSE_LOG, "w", encoding="utf-8") as f:
        json.dump(sorted(ids), f)


def run_reverse_scan(max_searches: int = 0, delay: float = 2.0):
    """
    Run the reverse scanner: search YouTube, collect IDs,
    check if any are English words.
    
    Args:
        max_searches: Max number of search queries (0 = all)
        delay: Delay between searches in seconds
    """
    from checker import load_results, save_results
    
    results = load_results()
    found_ids = {r["video_id"] for r in results}
    checked_ids = load_reverse_checked()
    
    all_ids_found = set()
    word_hits = []
    
    terms = list(SEARCH_TERMS)
    random.shuffle(terms)
    
    if max_searches > 0:
        terms = terms[:max_searches]
    
    total = len(terms)
    
    for i, term in enumerate(terms, 1):
        print(f"  [{i}/{total}] Searching: \"{term}\"...", end="", flush=True)
        
        ids = search_youtube_for_ids(term)
        new_ids = [vid for vid in ids if vid not in checked_ids]
        checked_ids.update(ids)
        all_ids_found.update(ids)
        
        hits_this_round = 0
        for vid in new_ids:
            analysis = is_word_like(vid)
            if analysis:
                hits_this_round += 1
                print(f"\n    *** WORD FOUND: {vid} = \"{analysis['readable']}\" ({analysis['type']})")
                
                # Get video details
                from checker import check_video
                video_info = check_video(vid)
                if video_info:
                    video_info["word_analysis"] = analysis
                    if vid not in found_ids:
                        results.append(video_info)
                        found_ids.add(vid)
                        save_results(results)
                        print(f"    Title: \"{video_info['title']}\" by {video_info['author']}")
        
        if hits_this_round == 0:
            print(f" {len(ids)} IDs ({len(new_ids)} new), no word-like IDs")
        
        save_reverse_checked(checked_ids)
        
        if delay > 0 and i < total:
            time.sleep(delay)
    
    print(f"\n  === REVERSE SCAN COMPLETE ===")
    print(f"  Total IDs examined: {len(all_ids_found)}")
    print(f"  Total unique IDs in database: {len(checked_ids)}")
    print(f"  Word-like hits: {len(word_hits)}")
    
    return word_hits


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Reverse YouTube word scanner")
    parser.add_argument("-n", "--max-searches", type=int, default=0)
    parser.add_argument("-d", "--delay", type=float, default=2.0)
    args = parser.parse_args()
    
    print("\n  YouTube Reverse Word Scanner")
    print("  Searching YouTube for videos, checking if IDs are words...\n")
    
    run_reverse_scan(
        max_searches=args.max_searches,
        delay=args.delay,
    )
