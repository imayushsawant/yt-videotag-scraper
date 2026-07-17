"""
YouTube Video Checker

Checks if a given 11-character string corresponds to a real, publicly
available YouTube video. Uses the oEmbed API (no API key required).
"""

import requests
import time
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

OEMBED_URL = "https://www.youtube.com/oembed"
RESULTS_FILE = Path(__file__).parent / "data" / "results.json"
CHECKED_FILE = Path(__file__).parent / "data" / "checked.json"


def _ensure_data_dir():
    """Ensure the data directory exists."""
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)


def check_video(video_id: str, timeout: float = 5.0) -> Optional[dict]:
    """
    Check if a YouTube video exists using oEmbed API.
    
    Returns video info dict if found, None otherwise.
    """
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        resp = requests.get(
            OEMBED_URL,
            params={"url": url, "format": "json"},
            timeout=timeout,
        )
        
        if resp.status_code == 200:
            data = resp.json()
            return {
                "video_id": video_id,
                "title": data.get("title", "Unknown"),
                "author": data.get("author_name", "Unknown"),
                "author_url": data.get("author_url", ""),
                "thumbnail": data.get("thumbnail_url", ""),
                "url": url,
                "found_at": datetime.now(timezone.utc).isoformat(),
                "phrase": video_id,
            }
        return None
    
    except requests.exceptions.RequestException:
        return None


def load_results() -> list[dict]:
    """Load previously found results."""
    _ensure_data_dir()
    if RESULTS_FILE.exists():
        try:
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_results(results: list[dict]):
    """Save results to JSON file."""
    _ensure_data_dir()
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def load_checked() -> set[str]:
    """Load set of already-checked video IDs."""
    _ensure_data_dir()
    if CHECKED_FILE.exists():
        try:
            with open(CHECKED_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except (json.JSONDecodeError, IOError):
            return set()
    return set()


def save_checked(checked: set[str]):
    """Save checked IDs to disk."""
    _ensure_data_dir()
    with open(CHECKED_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(checked), f)


def batch_check(
    video_ids: list[str],
    max_workers: int = 5,
    delay: float = 0.1,
    callback=None,
) -> list[dict]:
    """
    Check multiple video IDs concurrently.
    
    Args:
        video_ids: List of 11-char candidate strings
        max_workers: Number of parallel workers
        delay: Delay between submissions to avoid rate limiting
        callback: Optional callback(video_id, result_or_none, index, total)
    
    Returns:
        List of found video info dicts
    """
    found = []
    total = len(video_ids)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for i, vid in enumerate(video_ids):
            future = executor.submit(check_video, vid)
            futures[future] = (vid, i)
            if delay > 0:
                time.sleep(delay)
        
        for future in as_completed(futures):
            vid, idx = futures[future]
            try:
                result = future.result()
                if result:
                    found.append(result)
                if callback:
                    callback(vid, result, idx, total)
            except Exception as e:
                if callback:
                    callback(vid, None, idx, total)
    
    return found


if __name__ == "__main__":
    # Quick test with known video IDs
    test_ids = ["dQw4w9WgXcQ", "helloworld1", "GoodMorning"]
    for vid in test_ids:
        result = check_video(vid)
        if result:
            print(f"  ✓ {vid} → \"{result['title']}\" by {result['author']}")
        else:
            print(f"  ✗ {vid} → not found")
