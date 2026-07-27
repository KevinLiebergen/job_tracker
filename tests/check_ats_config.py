"""Validate config/companies.py without hitting the network.

Run with --live to additionally fetch every board and report how many are still up;
that takes a couple of minutes and is meant to be run occasionally, not on every commit.
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsers.ats import load_ats_parsers, PARSERS_BY_ATS, WorkdayParser, ComeetParser

REQUIRED_EXTRA = {WorkdayParser: ("wd", "site"), ComeetParser: ("company",)}


def check_config():
    parsers = load_ats_parsers()
    errors = []

    if not parsers:
        errors.append("COMPANIES produced no parsers")

    seen = {}
    for p in parsers:
        if not p.token:
            errors.append(f"{p.name}: empty token")
        for key in REQUIRED_EXTRA.get(type(p), ()):
            if not p.extra.get(key):
                errors.append(f"{p.name}: {p.ats} entry is missing '{key}'")

        # Two entries with the same name would be indistinguishable in notifications.
        if p.name in seen:
            errors.append(f"duplicate company name: {p.name}")
        seen[p.name] = p

        # build_urls must give something crawl() can pass straight to parse()
        urls = p.build_urls(["security"])
        if not urls or not str(urls[0]).startswith("http"):
            errors.append(f"{p.name}: build_urls returned {urls!r}")

    print(f"{len(parsers)} companies, {len(set(p.ats for p in parsers))} of "
          f"{len(PARSERS_BY_ATS)} ATS types in use")
    return parsers, errors


def check_live(parsers):
    """Fetch each board once and report failures — boards do get renamed or removed."""
    dead = []
    for i, p in enumerate(parsers, 1):
        try:
            jobs = p.parse(p.build_urls(None)[0], None)
            print(f"[{i:3}/{len(parsers)}] {p.name[:30]:32} {len(jobs):4} postings")
        except Exception as e:
            print(f"[{i:3}/{len(parsers)}] {p.name[:30]:32} FAILED {type(e).__name__}: {e}")
            dead.append(p.name)
    return dead


if __name__ == "__main__":
    parsers, errors = check_config()

    if "--live" in sys.argv:
        dead = check_live(parsers)
        if dead:
            print(f"\n{len(dead)} unreachable boards: {', '.join(dead)}")

    if errors:
        print("\nFAILURE: " + "\n         ".join(errors))
        sys.exit(1)
    print("SUCCESS: config/companies.py is valid.")
