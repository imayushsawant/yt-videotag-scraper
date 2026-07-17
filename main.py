"""
YouTube Word Scraper -- Main CLI

Generates meaningful English words/phrases, checks if they're real YouTube
video IDs, and collects the hits.
"""

import sys
import os
import time
import json
import signal
import argparse
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Fix encoding on Windows
if sys.platform == "win32":
    os.system("")  # Enable ANSI escape codes on Windows
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from wordgen import generate_candidates
from checker import check_video, load_results, save_results, load_checked, save_checked


# -- ANSI colors --
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    BG_GREEN = "\033[42m"
    BG_RED   = "\033[41m"


BANNER = f"""
{C.CYAN}{C.BOLD}
  +==============================================================+
  |                                                              |
  |   __   __ _____   __        __            _                  |
  |   \\ \\ / /|_   _| / /__  __ / /_ _ ___  __| |                 |
  |    \\ V /   | |  / / \\ \\/ // __| '_/ _ \\/ _` |                 |
  |     | |    | | / /   >  < | (_| | |  __/ (_| |                 |
  |     |_|    |_|/_/   /_/\\_\\ \\__|_|  \\___|\\__,_|                 |
  |                                                              |
  |   YouTube Video ID Word Hunter                               |
  |   Finding real videos with meaningful word IDs               |
  |                                                              |
  +==============================================================+
{C.RESET}"""


# Hand-crafted high-priority candidates that are most likely to be real video IDs
# These are natural-looking 11-character English words/phrases
PRIORITY_CANDIDATES = [
    # Natural PascalCase phrases (very likely someone used these)
    "GoodMorning", "NeverGiveUp", "KeepGoing",   "DontGiveUp",
    "HowAreYou",   "HelloWorld",  "ThankYou",     "GoodNight",
    "ImSoSorry",   "LetsGoHome",  "ComeWithMe",   "TrustInGod",
    "BelieveInMe", "DreamBigNow", "FollowYour",   "StayStrong",
    "HoldOnTight", "NeverAlone",  "BreakingBad",  "GameOfLife",
    "BackToLife",  "FindYourWay", "RunAwayNow",   "OpenYourEye",
    "CallMeBack",  "TakeItEasy",  "MakeItCount",  "FeelTheVibe",
    "LoveIsReal",  "LoveIsBlind", "BornToShine",  "RiseAndFall",
    "DayAndNight", "FireAndIce",  "BlackAndRed",  "LightAndDark",
    "StopAndGo",   "MindAndBody", "WordAndDeed",  "HeartAndSoul",
    "LifeIsGood",  "LifeIsHard",  "TimeToShine",  "ReadyToGo",
    "HereWeGoNow", "WhatIsLove",  "WhoAmIToday",  "WhyNotTryIt",
    "JustDoItNow", "GoForItNow",  "LetMeBeMe",    "SetMeFreeNow",
    "YouAndMeNow", "MeAndYouNow", "UsAndThem",    "HimAndHer",

    # CamelCase variants
    "goodMorning", "neverGiveUp", "keepGoing",    "helloWorld",
    "thankYou",    "goodNight",   "howAreYou",    "comeWithMe",
    "trustInGod",  "dreamBigNow", "stayStrong",   "holdOnTight",
    "neverAlone",  "breakingBad", "gameOfLife",   "backToLife",
    "findYourWay", "callMeBack",  "takeItEasy",   "feelTheVibe",
    "loveIsReal",  "loveIsBlind", "bornToShine",  "riseAndFall",
    "dayAndNight", "fireAndIce",  "lifeIsGood",   "timeToShine",
    "readyToGo",   "whatIsLove",  "justDoItNow",  "setMeFreeNow",

    # All lowercase natural phrases
    "goodmorning", "nevergiveup", "keepitreal",   "helloworld",
    "thankyou",    "goodnight",   "howareyou",    "comewithme",
    "trustingod",  "dreambignow", "staystrong",   "holdon tight",
    "neveralone",  "breakingbad", "gameoflife",   "backtolife",
    "findyourway", "callmeback",  "takeiteasy",   "feelthevibe",
    "loveisreal",  "loveisblind", "borntoshine",  "riseandfall",
    "dayandnight", "fireandice",  "lifeisgood",   "timetoshine",
    "readytogo",   "whatislove",  "justdoitnow",  "letmebefree",

    # ALL CAPS
    "GOODMORNING", "NEVERGIVEUP", "HELLOWORLD",   "THANKYOU",
    "GOODNIGHT",   "HOWAREYOU",   "STAYSTRONG",   "NEVERALONE",
    "BREAKINGBAD", "GAMEOFLIFE",  "BACKTOLIFE",   "TAKEITEASY",
    "LOVEISREAL",  "LIFEISGOOD",  "TIMETOSHINE",  "WHATISLOVE",

    # Mixed interesting combos
    "AwesomeDay",  "PerfectDay",  "BestDayEver",  "WorstDayEver",
    "SunnyDayOut", "RainyDayOut", "ColdDayOut",   "HotDayToday",
    "BigDreamsNow","NewLifeNow",  "OldFriendHi",  "LastDayHere",
    "FirstDayOut", "MyBestShot",  "OneMoreTime",  "OneLastTime",
    "OnceUponTime","HappyBirthd", "MerryXmasNow", "NewYearVibes",
    "SummerVibes", "WinterVibes", "SpringVibes",  "AutumnVibes",

    # Internet / meme culture
    "RickRollNow", "NyanCatLive", "EpicFailNow",  "EpicWinTime",
    "ClickMeNow",  "SubAndLike",  "LikeAndShare", "HitThatLike",

    # Philosophy / deep
    "ToBeOrNotTo", "IThinkIAmOk", "WeAreAllOne",  "AllIsVanity",
    "TruthIsHere", "BeTheChange", "StillIRise",   "KnowThyself",

    # Names + words
    "IAmTheGreat", "IAmLegendNow","IAmIronManOk",  "WeAreTheOne",

    # Music / art
    "PlayItAgain", "SingWithMe",  "DanceAllDay",  "MusicIsLife",
    "BeatDropNow", "RockAndRoll", "JazzItUpNow",  "SoulMusicOn",

    # Tech / gaming
    "CodeAndPlay", "HackTheCode", "DebugMyLife",  "PushToMain",
    "GitCommitOk", "StackedUp",   "LevelUpNow",   "BossLevelUp",
    "GameOverMan", "PlayerOneGo", "HighScoreUp",  "RespawnNow",

    # Food
    "CookWithLove","BakeACakeNow","PizzaTimeNow", "CoffeeBreak",
    "TeaTimeIsOn", "LunchTimeNow","BreakfastClub", "DinnerReady",

    # Travel
    "TravelWithMe","RoadTripNow", "FlyWithMeNow", "GoExploreIt",
    "WanderAround","LostAndFound","AroundTheMap",  "SeaAndSand",

    # Motivation
    "YouCanDoIt",  "BelieveMore", "KeepFighting", "NeverQuitIt",
    "PushHarder",  "GoGetItDone", "MakeItWork",   "WorkHardNow",
    "GetUpAndGo",  "MoveForward", "StandUpTall",  "FightForIt",

    # Simple words / descriptions (exactly 11 chars)
    "sunflowers",  "moonlighter", "nightlight",  "butterflies",
    "candlelight", "underground", "countryside",  "masterpiece",
    "fingerprint", "comfortable", "transparent",  "electricity",
    "information", "development", "independent",  "temperature",
    "performance", "imagination", "celebration",  "opportunity",
    "achievement", "personality", "photography",  "environment",
    "application", "destruction", "engineering",  "educational",

    # More natural word combos
    "ILoveMusic",  "ILovePizza",  "ILoveYouAll",  "IHateMonday",
    "GoHomeNow",   "StopItPlease","ShutUpPlease", "WakeUpEarly",
    "SleepWell",   "EatHealthy",  "RunFasterNow", "JumpHigherUp",
    "ThinkBigger", "ActNowFast",  "SpeakUpLoud",  "ListenClose",

    # YouTube-specific
    "SubscribeMe", "HitTheBell",  "TurnOnBells",  "LeaveALike",
    "DropAComment","ShareThisVid","WatchMePlay",  "StreamIsLive",
    "FirstVideo",  "LastVideoUp", "NewVideoOut",  "BestVideoUp",
]


# -- Statistics --
class Stats:
    def __init__(self):
        self.checked = 0
        self.found = 0
        self.errors = 0
        self.start_time = time.time()

    @property
    def elapsed(self) -> float:
        return time.time() - self.start_time

    @property
    def rate(self) -> float:
        if self.elapsed > 0:
            return self.checked / self.elapsed
        return 0.0

    def status_line(self) -> str:
        elapsed = self.elapsed
        mins, secs = divmod(int(elapsed), 60)
        hrs, mins = divmod(mins, 60)
        time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"

        return (
            f"  {C.DIM}[{time_str}]{C.RESET}  "
            f"{C.BLUE}Checked:{C.RESET} {C.BOLD}{self.checked:,}{C.RESET}  "
            f"{C.GREEN}Found:{C.RESET} {C.BOLD}{self.found}{C.RESET}  "
            f"{C.YELLOW}Rate:{C.RESET} {self.rate:.1f}/s  "
            f"{C.RED}Errors:{C.RESET} {self.errors}"
        )


# -- Main scanner --
def run_scanner(
    max_checks: int = 0,
    delay: float = 0.05,
    save_every: int = 50,
    workers: int = 8,
):
    """
    Main scanning loop with concurrent checking.

    Args:
        max_checks: Max number of IDs to check (0 = unlimited)
        delay: Delay between batch submissions in seconds
        save_every: Save progress every N checks
        workers: Number of concurrent worker threads
    """
    print(BANNER)

    # Load previous state
    results = load_results()
    checked = load_checked()
    found_ids = {r["video_id"] for r in results}

    print(f"  {C.CYAN}Previously checked:{C.RESET} {len(checked):,} IDs")
    print(f"  {C.GREEN}Previously found:{C.RESET}   {len(results)} videos")
    print(f"  {C.YELLOW}Workers:{C.RESET}             {workers}")
    print(f"  {C.YELLOW}Delay:{C.RESET}               {delay}s")
    if max_checks > 0:
        print(f"  {C.MAGENTA}Max checks:{C.RESET}          {max_checks:,}")
    print()
    print(f"  {C.DIM}Loading word list...{C.RESET}")

    stats = Stats()
    running = True

    def signal_handler(sig, frame):
        nonlocal running
        print(f"\n\n  {C.YELLOW}>> Stopping gracefully...{C.RESET}")
        running = False

    signal.signal(signal.SIGINT, signal_handler)

    # Build candidate iterator: priority candidates first, then generated ones
    def all_candidates():
        # Phase 0: Hand-crafted high-priority candidates
        priority = [c for c in PRIORITY_CANDIDATES if len(c) == 11]
        print(f"  {C.CYAN}Priority candidates:{C.RESET} {len(priority)}")
        for c in priority:
            yield c

        # Phase 1+: Generated candidates
        yield from generate_candidates()

    candidate_iter = all_candidates()
    print(f"  {C.DIM}Starting scan...{C.RESET}\n")
    print(f"  {C.DIM}{'-' * 60}{C.RESET}")

    try:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit batches of work
            pending = {}  # future -> candidate

            while running:
                if max_checks > 0 and stats.checked >= max_checks:
                    print(f"\n  {C.YELLOW}Reached max checks ({max_checks:,}){C.RESET}")
                    break

                # Fill the pool up to `workers` pending futures
                while len(pending) < workers:
                    try:
                        candidate = next(candidate_iter)
                    except StopIteration:
                        break

                    if candidate in checked or len(candidate) != 11:
                        continue

                    checked.add(candidate)
                    future = executor.submit(check_video, candidate)
                    pending[future] = candidate

                if not pending:
                    print(f"\n  {C.YELLOW}Exhausted all candidates.{C.RESET}")
                    break

                # Wait for at least one future to complete
                done_futures = []
                for future in list(pending.keys()):
                    if future.done():
                        done_futures.append(future)

                if not done_futures:
                    # Wait a tiny bit for futures to complete
                    time.sleep(0.01)
                    continue

                for future in done_futures:
                    candidate = pending.pop(future)
                    stats.checked += 1

                    try:
                        result = future.result()
                    except Exception:
                        stats.errors += 1
                        result = None

                    if result:
                        stats.found += 1
                        results.append(result)
                        found_ids.add(candidate)

                        # Print discovery with fanfare
                        print(f"\r  {' ' * 100}")
                        print(f"\r  {C.BG_GREEN}{C.WHITE}{C.BOLD} * HIT! * {C.RESET}")
                        print(f"  {C.GREEN}ID:{C.RESET}     {C.BOLD}{candidate}{C.RESET}")
                        print(f"  {C.GREEN}Title:{C.RESET}  {C.BOLD}{result['title']}{C.RESET}")
                        print(f"  {C.GREEN}Author:{C.RESET} {result['author']}")
                        print(f"  {C.GREEN}URL:{C.RESET}    https://youtube.com/watch?v={candidate}")
                        print(f"  {C.DIM}{'-' * 60}{C.RESET}")

                        # Save immediately on discovery
                        save_results(results)
                        save_checked(checked)
                    else:
                        # Print progress on same line
                        print(
                            f"\r  {C.DIM}x {candidate}{C.RESET}"
                            f"  {stats.status_line()}",
                            end="",
                            flush=True,
                        )

                    if max_checks > 0 and stats.checked >= max_checks:
                        break

                # Periodic save
                if stats.checked % save_every == 0:
                    save_checked(checked)

                # Small delay to avoid hammering
                if delay > 0:
                    time.sleep(delay)

            # Cancel remaining futures
            for future in pending:
                future.cancel()

    except KeyboardInterrupt:
        pass

    # Final save
    save_results(results)
    save_checked(checked)

    # Summary
    print(f"\n\n  {C.CYAN}{C.BOLD}=== SCAN COMPLETE ==={C.RESET}")
    print(f"  {stats.status_line()}")
    print(f"\n  {C.GREEN}Total videos found:{C.RESET} {C.BOLD}{len(results)}{C.RESET}")

    if results:
        print(f"\n  {C.CYAN}All discovered videos:{C.RESET}")
        for r in results:
            print(f"    {C.GREEN}*{C.RESET} {C.BOLD}{r['video_id']}{C.RESET} -> \"{r['title']}\"")

    print(f"\n  {C.DIM}Results saved to: data/results.json{C.RESET}")
    print(f"  {C.DIM}Run the web dashboard: python app.py{C.RESET}\n")


def main():
    parser = argparse.ArgumentParser(
        description="YouTube Video ID Word Hunter -- Find real videos with meaningful word IDs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  Forward (default):  Generate English words -> check if they're video IDs
  Reverse (-r):       Search YouTube -> check if video IDs are English words
  Both (--both):      Run reverse scan first, then forward scan

Examples:
  python main.py                     # Forward scan (unlimited, 8 workers)
  python main.py -n 2000             # Forward scan, 2000 checks
  python main.py -r                  # Reverse scan (all search terms)
  python main.py -r -n 20            # Reverse scan, 20 search queries
  python main.py --both -n 1000      # Both modes
  python main.py -w 12 -d 0.02      # Fast forward scan
        """,
    )
    parser.add_argument(
        "-n", "--max-checks",
        type=int,
        default=0,
        help="Max checks (forward) or max searches (reverse). 0 = unlimited.",
    )
    parser.add_argument(
        "-d", "--delay",
        type=float,
        default=0.05,
        help="Delay between cycles in seconds (default: 0.05 forward, 2.0 reverse)",
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=8,
        help="Number of concurrent worker threads (default: 8, forward only)",
    )
    parser.add_argument(
        "-r", "--reverse",
        action="store_true",
        help="Run reverse scan: search YouTube, check if video IDs are words",
    )
    parser.add_argument(
        "--both",
        action="store_true",
        help="Run both reverse and forward scans",
    )
    parser.add_argument(
        "--save-every",
        type=int,
        default=50,
        help="Save progress every N checks (default: 50)",
    )

    args = parser.parse_args()

    if args.reverse or args.both:
        from reverse_scanner import run_reverse_scan
        print(BANNER)
        print(f"  {C.CYAN}{C.BOLD}=== REVERSE SCAN MODE ==={C.RESET}")
        print(f"  {C.DIM}Searching YouTube for videos, checking if IDs are words...{C.RESET}\n")
        reverse_delay = args.delay if args.delay != 0.05 else 2.0
        run_reverse_scan(
            max_searches=args.max_checks if not args.both else 0,
            delay=reverse_delay,
        )
        if not args.both:
            return
        print(f"\n  {C.CYAN}{C.BOLD}=== NOW RUNNING FORWARD SCAN ==={C.RESET}\n")

    run_scanner(
        max_checks=args.max_checks,
        delay=args.delay,
        save_every=args.save_every,
        workers=args.workers,
    )


if __name__ == "__main__":
    main()

