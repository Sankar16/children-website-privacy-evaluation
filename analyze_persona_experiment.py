#!/usr/bin/env python3
import sqlite3
from pathlib import Path
import re

import pandas as pd
import tldextract

# ======================================================
# 1. CONFIG
# ======================================================

BASE_DIR = Path(__file__).resolve().parent

# We expect dirs like:
#   datadir_child_persona_only_run1
#   datadir_adult_persona_only_run2
#   datadir_child_same_sites_run1
#   datadir_adult_same_sites_run1
# each containing: crawl-data.sqlite

PERSONAS = ["child", "adult"]
CONDITIONS = ["persona_only", "same_sites"]

# IMPORTANT: same tracker list you used in deeper_trackers.py
TRACKER_DOMAINS = {
    "doubleclick.net",
    "google-analytics.com",
    "googletagmanager.com",
    "googlesyndication.com",
    "facebook.com",
    "facebook.net",
    "adnxs.com",
    "scorecardresearch.com",
    "criteo.com",
    "twitter.com",
    "youtube.com",
}


# ======================================================
# 2. HELPERS
# ======================================================

def extract_domain(url: str) -> str:
    if not url:
        return ""
    ext = tldextract.extract(url)
    return ext.registered_domain or ""


def load_http_requests(db_path: Path) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    # Be defensive in case schema ever changes
    # but OpenWPM 0.31 has these columns.
    q = """
        SELECT
            visit_id,
            url,
            top_level_url
        FROM http_requests
    """
    df = pd.read_sql_query(q, conn)
    conn.close()
    return df


def annotate_requests(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["site_domain"] = df["top_level_url"].apply(extract_domain)
    df["request_domain"] = df["url"].apply(extract_domain)

    df["is_third_party"] = (
        (df["request_domain"] != "") &
        (df["site_domain"] != "") &
        (df["request_domain"] != df["site_domain"])
    ).astype(int)

    df["is_tracker"] = df["request_domain"].isin(TRACKER_DOMAINS)
    return df


def discover_db_files() -> list[tuple[str, str, int, Path]]:
    """
    Return a list of (persona, condition, run_id, db_path)
    by globbing datadir_* folders.
    """
    results = []
    for persona in PERSONAS:
        for condition in CONDITIONS:
            pattern = f"datadir_{persona}_{condition}_run*"
            for datadir in BASE_DIR.glob(pattern):
                if datadir.is_dir():
                    m = re.search(r"run(\d+)$", datadir.name)
                    if not m:
                        continue
                    run_id = int(m.group(1))
                    db_path = datadir / "crawl-data.sqlite"
                    if db_path.exists():
                        results.append((persona, condition, run_id, db_path))
    return sorted(results, key=lambda x: (x[1], x[0], x[2]))  # sort by condition, persona, run


# ======================================================
# 3. MAIN ANALYSIS
# ======================================================

def main():
    discovered = discover_db_files()
    if not discovered:
        print("No crawl-data.sqlite files found for the expected patterns.")
        print("Expected something like datadir_child_persona_only_run1/crawl-data.sqlite")
        return

    print("Found crawl databases:")
    for persona, condition, run_id, db_path in discovered:
        print(f"  persona={persona:5s} | condition={condition:11s} | run={run_id} | {db_path}")

    all_rows = []

    # Load + annotate all runs into one big DataFrame
    for persona, condition, run_id, db_path in discovered:
        df = load_http_requests(db_path)
        df = annotate_requests(df)
        df["persona"] = persona
        df["condition"] = condition
        df["run_id"] = run_id
        all_rows.append(df)

    if not all_rows:
        print("No HTTP request rows loaded from databases.")
        return

    df_all = pd.concat(all_rows, ignore_index=True)

    # -------------------------
    # 3.1 Aggregate per persona + condition
    # -------------------------
    summaries = []
    for (persona, condition), group in df_all.groupby(["persona", "condition"]):
        total_http = len(group)
        third_party = group[group["is_third_party"] == 1]
        trackers = third_party[third_party["is_tracker"]]

        third_party_count = len(third_party)
        tracker_count = len(trackers)

        unique_sites = group["top_level_url"].nunique()
        unique_tracker_domains = trackers["request_domain"].nunique()

        tp_ratio = (third_party_count / total_http) if total_http > 0 else 0.0
        tr_ratio = (tracker_count / total_http) if total_http > 0 else 0.0

        summaries.append(
            {
                "persona": persona,
                "condition": condition,
                "total_http": total_http,
                "third_party_requests": third_party_count,
                "tracker_requests": tracker_count,
                "tp_ratio": tp_ratio,
                "tr_ratio": tr_ratio,
                "unique_sites": unique_sites,
                "unique_tracker_domains": unique_tracker_domains,
            }
        )

    summary_df = pd.DataFrame(summaries).sort_values(
        ["condition", "persona"]
    )
    out_persona = BASE_DIR / "persona_condition_summary.csv"
    summary_df.to_csv(out_persona, index=False)
    print(f"\nSaved persona+condition summary to: {out_persona}")

    # Pretty-print summary
    print("\n=== Persona / Condition Summary ===")
    for condition in CONDITIONS:
        cond_df = summary_df[summary_df["condition"] == condition]
        if cond_df.empty:
            continue
        print(f"\n--- Condition: {condition} ---")
        for _, row in cond_df.iterrows():
            print(
                f"Persona={row['persona']:5s} | "
                f"Total={row['total_http']:6d} | "
                f"3P={row['third_party_requests']:6d} ({row['tp_ratio']:.1%}) | "
                f"Trackers={row['tracker_requests']:5d} ({row['tr_ratio']:.1%}) | "
                f"Sites={row['unique_sites']:4d} | "
                f"Tracker domains={row['unique_tracker_domains']:3d}"
            )

    # -------------------------
    # 3.2 Site-level intensity
    # -------------------------
    tp = df_all[df_all["is_third_party"] == 1].copy()
    trackers = tp[tp["is_tracker"]].copy()

    # For each persona/condition/site: how many 3P and tracker requests?
    site_intensity = (
        tp.groupby(["condition", "persona", "top_level_url"])
        .agg(
            total_tp_requests=("url", "count"),
            tracker_requests=("is_tracker", "sum"),
        )
        .reset_index()
    )

    tracker_domains_per_site = (
        trackers.groupby(["condition", "persona", "top_level_url"])["request_domain"]
        .nunique()
        .rename("unique_tracker_domains")
    )

    site_intensity = site_intensity.merge(
        tracker_domains_per_site,
        on=["condition", "persona", "top_level_url"],
        how="left",
    )

    site_intensity["unique_tracker_domains"] = (
        site_intensity["unique_tracker_domains"].fillna(0).astype(int)
    )

    out_site = BASE_DIR / "site_tracker_intensity_by_condition.csv"
    site_intensity.to_csv(out_site, index=False)
    print(f"Saved site-level tracker intensity to: {out_site}")

    # -------------------------
    # 3.3 Tracker-domain stats per persona+condition
    # -------------------------
    if not trackers.empty:
        tracker_stats = (
            trackers.groupby(["condition", "persona", "request_domain"])
            .agg(
                total_requests=("url", "count"),
                num_sites=("top_level_url", "nunique"),
            )
            .reset_index()
            .rename(columns={"request_domain": "tracker_domain"})
        )

        # Compute share of 3P for each persona+condition
        tp_counts = (
            tp.groupby(["condition", "persona"])["url"]
            .count()
            .rename("total_tp_for_group")
        )

        tracker_stats = tracker_stats.merge(
            tp_counts,
            on=["condition", "persona"],
            how="left",
        )
        tracker_stats["share_of_third_party_requests"] = (
            tracker_stats["total_requests"] / tracker_stats["total_tp_for_group"]
        )

        out_trackers = BASE_DIR / "tracker_by_persona_condition.csv"
        tracker_stats.to_csv(out_trackers, index=False)
        print(f"Saved per-tracker stats by persona+condition to: {out_trackers}")

        # Nice console output: top trackers per condition/persona
        print("\n=== Top trackers per condition/persona (by #requests) ===")
        for condition in CONDITIONS:
            for persona in PERSONAS:
                sub = tracker_stats[
                    (tracker_stats["condition"] == condition)
                    & (tracker_stats["persona"] == persona)
                ]
                if sub.empty:
                    continue
                sub_sorted = sub.sort_values("total_requests", ascending=False).head(5)
                print(f"\nCondition={condition}, Persona={persona}")
                for _, row in sub_sorted.iterrows():
                    print(
                        f"  {row['tracker_domain']:<30} "
                        f"requests={row['total_requests']:<5d}  "
                        f"sites={row['num_sites']:<4d}  "
                        f"share_of_3p={row['share_of_third_party_requests']:.1%}"
                    )
    else:
        print("\nNo tracker requests found at all – tracker_stats not created.")


if __name__ == "__main__":
    main()