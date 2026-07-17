"""
YouTube Word Scraper — Web Dashboard

A beautiful web UI to browse discovered YouTube videos
that have meaningful English word IDs.
"""

import json
from pathlib import Path
from flask import Flask, render_template, jsonify

app = Flask(__name__)

DATA_DIR = Path(__file__).parent / "data"
RESULTS_FILE = DATA_DIR / "results.json"
CHECKED_FILE = DATA_DIR / "checked.json"


def get_results() -> list[dict]:
    """Load results from JSON."""
    if RESULTS_FILE.exists():
        try:
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def get_checked_count() -> int:
    """Get number of checked IDs."""
    if CHECKED_FILE.exists():
        try:
            with open(CHECKED_FILE, "r", encoding="utf-8") as f:
                return len(json.load(f))
        except (json.JSONDecodeError, IOError):
            return 0
    return 0


@app.route("/")
def index():
    """Main dashboard page."""
    results = get_results()
    checked_count = get_checked_count()
    return render_template(
        "index.html",
        results=results,
        total_found=len(results),
        total_checked=checked_count,
    )


@app.route("/api/results")
def api_results():
    """API endpoint for results (for dynamic updates)."""
    results = get_results()
    checked_count = get_checked_count()
    return jsonify({
        "results": results,
        "total_found": len(results),
        "total_checked": checked_count,
    })


if __name__ == "__main__":
    import sys
    import os
    if sys.platform == "win32":
        os.system("")
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print("\n  [YouTube Word Scraper Dashboard]")
    print("  ---------------------------------")
    print("  Open: http://localhost:5000\n")
    app.run(debug=True, port=5000)
