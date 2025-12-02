# Ads and Tracking Analysis on Children's Websites

This repository contains the code and experiments for our project:

> **"Ads Analysis on Children Websites"**  
> conducted in collaboration with **North Carolina State University (NC State)** as part of a privacy-focused research course.

We study how much **tracking and advertising** children encounter on popular kids’ websites, and how well these sites align with **COPPA-style** privacy expectations.  
The project has two main components:

1. **Static Privacy Audit (Python scraper)**
2. **Dynamic Tracking Measurement (OpenWPM with child/adult personas)**

---

## Project Overview

### 1. Static Privacy Audit (`extract.py`)

We built an automated Python pipeline that performs a **static analysis** of ~40 child-directed websites.

For each site, the script:

- Fetches the HTML using a realistic browser User-Agent.
- Extracts **third-party domains** from:
  - `<script>`, `<iframe>`, `<img>`, `<link>`, and media tags.
  - Raw HTML URLs using regex.
- Detects **advertising indicators**, based on:
  - Class names / IDs containing `ad`, `advertisement`, `sponsor`, `promo`, `banner`, etc.
  - Ad-like iframes and external script URLs.
- Computes a **child-friendly UI score**, using:
  - Large/interactive buttons
  - Playful/educational language (“fun”, “play”, “game”, “learn”, etc.)
  - Rich visual content (images/videos)
  - Simple navigation and minimal forms
- Estimates **COPPA-style compliance**, checking for:
  - Presence of a privacy policy
  - Mentions of children/parents/guardians
  - Parental consent language
  - Data collection / disclosure descriptions
  - Age verification cues
  - Data minimization (no obvious sensitive fields)
  - Limited third-party domains
  - Absence of behavioral advertising

The script outputs a CSV scorecard:

- **`website_privacy_audit_automated.csv`**

with per-site metrics such as:

- Number of third-party domains
- Ads present / likely / none
- Child-friendly UI label + score
- COPPA score + % and compliance flag
- COPPA issues (missing privacy policy, no child section, no consent, etc.)

---

### 2. Dynamic Tracking with OpenWPM

We use **[OpenWPM](https://github.com/openwpm/OpenWPM)** to capture *real browser* behavior and reveal what happens “behind the scenes” when pages load.

There are two scripts:

- `crawl_persona_final.py` – runs the crawling experiment
- `analyze_persona_experiment.py` – analyzes the OpenWPM logs

#### Personas

We simulate two browser personas using different User-Agents:

- **Child persona**
  - iPad / mobile-style UA
  - Visits **children’s websites** in persona-only condition
- **Adult persona**
  - Desktop Chrome UA  
  - Visits **adult/general-interest sites** in persona-only condition

#### Conditions

We run two experimental conditions:

1. **Persona-only condition**
   - Child persona → child sites list  
   - Adult persona → adult/general sites list  
   - Run multiple times for robustness.

2. **Same-sites condition**
   - Both child and adult personas visit the **same set** of popular mainstream sites  
     (Google, YouTube, Amazon, Reddit, Netflix, Instagram, etc.)

#### What OpenWPM Records

For each visit, OpenWPM logs to `crawl-data.sqlite`:

- All **HTTP requests**
- Top-level URL (site URL)
- Request URL and domain
- First-party vs **third-party** classification
- Whether the request domain is a **known tracker**, using a curated list:
  - `doubleclick.net`, `google-analytics.com`, `googletagmanager.com`,
    `googlesyndication.com`, `facebook.com`, `facebook.net`, `adnxs.com`,
    `scorecardresearch.com`, `criteo.com`, `twitter.com`, `youtube.com`, etc.

#### Analysis Outputs

`analyze_persona_experiment.py`:

- Scans all `datadir_*` folders created by the crawl
- Loads `http_requests` tables from each `crawl-data.sqlite`
- Annotates each request as:
  - First-party / third-party
  - Tracker / non-tracker
- Aggregates statistics per `(persona, condition)`:

Produces the following CSVs:

- **`persona_condition_summary.csv`**
  - Total HTTP requests
  - Third-party requests and %
  - Tracker requests and %
  - Unique sites
  - Unique tracker domains

- **`site_tracker_intensity_by_condition.csv`**
  - Per-site 3rd-party and tracker counts

- **`tracker_by_persona_condition.csv`**
  - Per-tracker-domain stats:
    - Total requests
    - Number of sites
    - Share of all third-party requests

These outputs are used to generate the figures and tables in our report.

---
Setup

1. Create and Activate Virtual Environment

Using conda (recommended):
conda create -n kids-privacy python=3.11
conda activate kids-privacy
Or with venv:
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate

2. Install Python Dependencies

pip install -r requirements.txt

3. System Requirements for OpenWPM

OpenWPM uses a real browser (Firefox) under the hood. Make sure you have:
- Firefox installed
- Geckodriver available in your PATH (often installable via your OS package manager)

On macOS, a common pattern is:
example using Homebrew
brew install --cask firefox
brew install geckodriver

On Linux / Windows, follow the official geckodriver installation instructions.

Note (macOS):
If you see issues related to fork / sandboxing, export:
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
before running OpenWPM scripts.

How to Run

A. Static Privacy Audit

This uses extract.py to crawl the curated list of ~40 children’s websites.
python extract.py

What it does:
- Crawls each site in the websites list inside extract.py
- Performs HTML-based static checks (third-party domains, ads, UI, COPPA signals)
- Writes results to: website_privacy_audit_automated.csv

B. Dynamic Tracking Experiment (OpenWPM)

1. Crawl with Personas
python crawl_persona_final.py

This script:
- Sets up OpenWPM browser instrumentation.
- Creates directories like:
- datadir_child_persona_only_run1
- datadir_adult_persona_only_run1
- datadir_child_persona_only_run2
- datadir_adult_persona_only_run2
- datadir_child_same_sites_run1
- datadir_adult_same_sites_run1
- For each (persona, condition, run):
- Visits all sites in the corresponding list
- Waits a few seconds on each page
- Logs HTTP traffic to crawl-data.sq

2. Analyze OpenWPM Logs
python analyze_persona_experiment.py

This script:
- Discovers all datadir_* folders under the project directory.
- Loads crawl-data.sqlite from each.
- Computes per-persona and per-condition metrics.
- Outputs:
persona_condition_summary.csv
site_tracker_intensity_by_condition.csv
tracker_by_persona_condition.csv

Ethics and Usage Notice

This project is intended for research and educational purposes only.
- Please respect each website’s robots.txt and terms of service.
- Do not use this code to perform high-frequency or abusive crawling.
- If you adapt this project, consider adding rate limiting and additional safeguards.

Credits

This project was developed by:
- Sai Vineel Reddy Marreddy – static analysis, third-party / ads / UI / COPPA pipeline
- Yaswanth Mullamuri – static analysis, scoring design, and data processing
- FNU Sankar Raghuthaman – OpenWPM experiment design, crawling scripts
- - Ravi Pavuluri – OpenWPM deployment, tracker analytics
with support and guidance from North Carolina State University.
