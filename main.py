import argparse
from crawler import crawl
from notifier import send_new_jobs
from database import init_db

from parsers.google import GoogleParser
from parsers.amazon import AmazonParser
from parsers.cloudflare import CloudflareParser
from parsers.microsoft import MicrosoftParser
from parsers.brave import BraveParser
from parsers.censys import CensysParser
from parsers.trend_micro import TrendMicroParser
from parsers.meta import MetaParser
from parsers.crowdstrike import CrowdstrikeParser
from parsers.paypal import PayPalParser
from parsers.palo_alto import PaloAltoParser
from parsers.gen import GenParser
from parsers.netflix import NetflixParser
from parsers.spotify import SpotifyParser

def load_urls():
    with open("urls.txt") as f:
        return [line.strip() for line in f if line.strip()]


def main(keywords, exclude=None):
    init_db()

    parsers = [
        GoogleParser(),
        AmazonParser(),
        CloudflareParser(),
        MicrosoftParser(),
        BraveParser(),
        CensysParser(),
        TrendMicroParser(),
        MetaParser(),
        CrowdstrikeParser(),
        PayPalParser(),
        PaloAltoParser(),
        GenParser(),
        NetflixParser(),
        SpotifyParser(),
    ]

    new_jobs = crawl(parsers, keywords, exclude)

    if new_jobs:
        print(f"\n📨 Sending {len(new_jobs)} new jobs to Telegram…")
        send_new_jobs(new_jobs)
    else:
        print("\n✔ No new jobs today.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Job tracker script")
    parser.add_argument("--keywords","-k",
                        nargs="+",  # Allows passing keywords splited by space
                        help="Keyword list to search",
                        default=["cybercrime",
                                 "security research",
                                 "research intern",
                                 "internship",
                                 "PhD",
                                 "Ph.D."]
                        )
    parser.add_argument("--exclude", "-e",
                        nargs="+",
                        help="Keywords to exclude from results",
                        default=[])
    args = parser.parse_args()
    main(args.keywords, args.exclude)
