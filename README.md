# YouTube Video ID Word Hunter 

Welcome to the **YouTube Video ID Word Hunter**! This was built as a fun "curiosity kills the cat" project to explore a fascinating question: *Are there any YouTube videos whose 11-character unique IDs happen to spell out actual English words or meaningful phrases?*

*(e.g., `https://youtube.com/watch?v=HelloWorld` or `https://youtube.com/watch?v=NeverGiveUp`)*

This repository contains tools to find these incredibly rare artifacts by testing specific meaningful phrases and performing reverse searches.

## Why was this built?

It started with a simple thought experiment: If you randomly typed in characters for a YouTube video URL, what are the chances you'd find a video? And even more interestingly, what if you typed a real phrase? 

We often see URLs like `?v=dQw4w9WgXcQ`, but finding one that reads `?v=SubscribeMe` feels like finding a needle in a haystack—or more accurately, a specific needle in a galaxy of haystacks.

## The Mathematics of YouTube IDs (Why brute-forcing is impossible) 

Before you try to brute-force randomly guess video IDs to find hidden or unlisted videos, let's look at the math. **It is statistically impossible to find random unlisted videos by blind guessing.**

### The Numbers

*   **Format**: A YouTube video ID is exactly **11 characters** long.
*   **Character Set**: It uses a Base64-like alphabet: `A-Z` (26), `a-z` (26), `0-9` (10), `-` (dash), and `_` (underscore). 
*   **Total Characters**: $26 + 26 + 10 + 2 = 64$ possible characters for every position.
*   **Total Possible Combinations**: $64^{11}$

$$ 64^{11} = 73,786,976,294,838,206,464 $$

That is **73.7 quintillion** possible video IDs.

### The Time Problem

To understand how massive this number is, let's assume you have a super-fast scraper that doesn't get rate-limited or IP-banned by Google. 

*   Assume you can check **10,000 video IDs per second** (which is impossible without severe blocking).
*   In one year, you would check: $10,000 \times 60 \times 60 \times 24 \times 365 = \approx 315.3 \text{ billion}$ checks.

To check every single possible YouTube ID at that blazing speed, it would take:
**~234,000,000 (234 million) years.**

Even if YouTube had **10 billion ($10^{10}$)** active videos, the probability of finding a single valid video by generating one random 11-character string is:
$10^{10} / (7.37 \times 10^{19}) \approx 0.000000000135$ (or a **1 in 7.37 billion chance**).

If you were doing 100 random checks a second, it would take you roughly **2.3 years** of continuous guessing just to have a coin-flip chance of finding *one* valid video. 

### Conclusion
Brute-forcing YouTube for random/unlisted videos is a mathematical dead end. 

That is exactly why this project uses a targeted approach instead of random brute-forcing. We specifically hunt for IDs that form real words (like `NeverGiveUp`) because humans love patterns, and finding one is a fun statistical anomaly!

## How It Works

The program operates in a few modes:

1.  **Forward Scan**: Generates a massive list of 11-character English words, phrases, or names (e.g., `CodeAndPlay`, `GoodMorning`) and checks if a video actually exists at that URL.
2.  **Reverse Scan**: Searches YouTube for videos and checks if the randomly generated ID attached to the video happens to be composed of recognizable English words.

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Forward Scan (Unlimited, default 8 workers)
python main.py

# Run with a max limit
python main.py -n 2000

# Run Reverse Scan
python main.py -r

# Run both modes
python main.py --both -n 1000
```

*Disclaimer: This is purely a curiosity-driven project. It respects YouTube's public endpoints. Please do not use this to hammer YouTube servers excessively; you will get rate-limited.*
