#!/usr/bin/env python3
import random
from pathlib import Path

from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import GetCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.task_manager import TaskManager


# ==============================
# 1. CONFIG
# ==============================

BASE_DIR = Path(__file__).resolve().parent

# How many times to repeat each condition?
RUNS_PERSONA_ONLY = 2   # child-sites-for-child, adult-sites-for-adult
RUNS_SAME_SITES = 1     # same site list for both personas

NUM_BROWSERS = 1
PAGE_LOAD_TIMEOUT = 60          # seconds
PAGE_SLEEP_SECONDS = 8          # time to “stay” on each page (GetCommand sleep)

# Persona user agents
CHILD_UA = (
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "CriOS/91.0.4472.77 Mobile/15E148 Safari/604.1"
)

ADULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


# ==============================
# 2. SITE LISTS
# ==============================

CHILD_SITES_PERSONA_ONLY = [
     "https://pbskids.org",
    "https://www.nickjr.com",
    "https://disneyjunior.disney.com",
    "https://www.sesamestreet.org",
    "https://kids.nationalgeographic.com",
    "https://www.abcya.com",
    "https://www.starfall.com",
    "https://www.funbrain.com",
    "https://www.poptropica.com",
    "https://www.cartoonnetwork.com",
    "https://www.highlightskids.com",
    "https://kids.scholastic.com",
    "https://www.crayola.com",
    "https://kids.lego.com",
    "https://www.fisher-price.com",
    "https://www.coolmathgames.com",
    "https://www.brainpop.com",
    "https://www.funology.com",
    "https://www.switchzoo.com",
    "https://www.nwf.org/Kids",
    "https://www.abcmouse.com",
    "https://www.education.com",
    "https://www.turtlediary.com",
    "https://www.roomrecess.com",
    "https://www.splashlearn.com",
    "https://www.e-learningforkids.org",
    "https://www.coolkidfacts.com",
    "https://kids.nationalgeographic.com/littlekids",
    "https://www.nasa.gov/kidsclub",
    "https://www.dkfindout.com",
    "https://www.storylineonline.net",
    "https://abc.com/shows/abc-kids",
    "https://www.safekidgames.com",
    "https://kids.poki.com",
    "https://www.owlieboo.com",
    "https://www.happyclicks.net",
    "https://www.gamesgames.com/games/kids-games",
    "https://www.boomerangtv.co.uk/games",
    "https://kids.nationalgeographic.com/games",
    "https://www.timeforkids.com",
]

# Adult-oriented / general news, careers, lifestyle, shopping, finance…
ADULT_SITES_PERSONA_ONLY = [
    "https://www.nytimes.com/",
    "https://www.cnn.com/",
    "https://www.bbc.com/",
    "https://www.wsj.com/",
    "https://www.bloomberg.com/",
    "https://www.theguardian.com/",
    "https://www.foxnews.com/",
    "https://www.nbcnews.com/",
    "https://www.reuters.com/",
    "https://www.economist.com/",
    "https://www.indeed.com/",
    "https://www.linkedin.com/",
    "https://www.glassdoor.com/",
    "https://www.monster.com/",
    "https://www.elle.com/",
    "https://www.menshealth.com/",
    "https://www.vogue.com/",
    "https://www.cosmopolitan.com/",
    "https://www.healthline.com/",
    "https://www.webmd.com/",
    "https://www.espn.com/",
    "https://www.si.com/",
    "https://www.tripadvisor.com/",
    "https://www.airbnb.com/",
    "https://www.booking.com/",
    "https://www.zillow.com/",
    "https://www.redfin.com/",
    "https://www.bankofamerica.com/",
    "https://www.chase.com/",
    "https://www.nerdwallet.com/",
    "https://www.macys.com/",
    "https://www.target.com/",
    "https://www.walmart.com/",
    "https://www.bestbuy.com/",
    "https://www.netflix.com/",
    "https://www.hulu.com/",
    "https://www.spotify.com/",
    "https://medium.com/",
    "https://www.quora.com/",
]

SAME_SITES = [
    "https://www.google.com/",
    "https://www.youtube.com/",
    "https://www.amazon.com/",
    "https://www.wikipedia.org/",
    "https://www.reddit.com/",
    "https://www.yahoo.com/",
    "https://www.imdb.com/",
    "https://www.ebay.com/",
    "https://www.spotify.com/",
    "https://www.netflix.com/",
    "https://www.instagram.com/",
    "https://www.tiktok.com/",
    "https://www.twitter.com/",
    "https://www.microsoft.com/",
    "https://www.apple.com/",
]


# ==============================
# 3. HELPERS
# ==============================

def build_manager_and_browsers(data_dir: Path, persona: str):
    """
    Create ManagerParams + BrowserParams using the current OpenWPM API.
    """
    data_dir.mkdir(parents=True, exist_ok=True)

    manager_params = ManagerParams(num_browsers=NUM_BROWSERS)
    manager_params.data_directory = data_dir
    manager_params.log_path = data_dir / "openwpm.log"

    browser_params = [BrowserParams(display_mode="native") for _ in range(NUM_BROWSERS)]
    for bp in browser_params:
        # Turn on instrumentation at the browser level
        bp.http_instrument = True
        bp.cookie_instrument = True
        bp.js_instrument = True
        bp.navigation_instrument = True
        bp.dns_instrument = True
        bp.save_content = False

        # Persona-specific user agent
        if persona == "child":
            bp.user_agent = CHILD_UA
        else:
            bp.user_agent = ADULT_UA

    return manager_params, browser_params


def crawl_sites_once(persona: str,
                     condition: str,
                     run_id: int,
                     sites,
                     data_root: Path):
    """
    Crawl a given list of sites once for a given persona + condition + run.
    Creates a separate datadir for each (persona, condition, run) combination.
    """
    datadir_name = f"datadir_{persona}_{condition}_run{run_id}"
    data_dir = data_root / datadir_name

    print(
        f"\n=== Run {run_id} | persona={persona} | "
        f"condition={condition} | sites={len(sites)} ==="
    )
    print(f"Data directory: {data_dir}")

    manager_params, browser_params = build_manager_and_browsers(data_dir, persona)

    # NEW: pass SQLiteStorageProvider to TaskManager (required in your version)
    structured_storage = SQLiteStorageProvider(data_dir / "crawl-data.sqlite")
    unstructured_storage = None  # you’re not storing raw HTML/screenshots here

    with TaskManager(
        manager_params,
        browser_params,
        structured_storage,
        unstructured_storage,
    ) as manager:

        for index, url in enumerate(sites):
            print(
                f"[{persona} | {condition} | run={run_id}] "
                f"({index+1}/{len(sites)}) Visiting: {url}"
            )

            def callback(success: bool, val: str = url) -> None:
                print(
                    f"    CommandSequence for {val} ran "
                    f"{'successfully' if success else 'UNSUCCESSFULLY'}"
                )

            cs = CommandSequence(
                url,
                site_rank=index,
                callback=callback,
            )

            # Use the *new* API: append_command + manager.execute_command_sequence
            sleep_time = PAGE_SLEEP_SECONDS + random.uniform(-2, 2)
            cs.append_command(
                GetCommand(url=url, sleep=max(1, int(sleep_time))),
                timeout=PAGE_LOAD_TIMEOUT,
            )

            manager.execute_command_sequence(cs)

    print(f"=== Finished persona={persona} | condition={condition} | run={run_id} ===")
    print(f"Data stored in: {data_dir}\n")


# ==============================
# 4. MAIN EXPERIMENT LOGIC
# ==============================

def main():
    # A) Persona-only condition: child→child sites, adult→adult sites
    for run in range(1, RUNS_PERSONA_ONLY + 1):
        for persona in ("child", "adult"):
            if persona == "child":
                sites = CHILD_SITES_PERSONA_ONLY
            else:
                sites = ADULT_SITES_PERSONA_ONLY

            crawl_sites_once(
                persona=persona,
                condition="persona_only",
                run_id=run,
                sites=sites,
                data_root=BASE_DIR,
            )

    # B) Same-sites condition: both personas visit SAME_SITES
    for run in range(1, RUNS_SAME_SITES + 1):
        for persona in ("child", "adult"):
            crawl_sites_once(
                persona=persona,
                condition="same_sites",
                run_id=run,
                sites=SAME_SITES,
                data_root=BASE_DIR,
            )


if __name__ == "__main__":
    main()