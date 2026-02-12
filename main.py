import argparse
import os

# Silence webdriver_manager logs
os.environ['WDM_LOG'] = '0'

from src.crawler import crawl
from src.notifier import send_new_jobs
from src.database import init_db, get_latest_jobs
from src.driver_factory import get_driver

from parsers.google import GoogleParser
from parsers.google_deep_mind import GoogleDeepMindParser
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
from parsers.cisco import CiscoParser
from parsers.anthropic import AnthropicParser
from parsers.datadog import DatadogParser


import logging

def main(keywords, exclude=None, verbose=False, list_jobs=False):
    init_db()

    if list_jobs:
        jobs = get_latest_jobs()
        print(f"📋 Last {len(jobs)} jobs found:\n")
        for job in jobs:
            title, company, location, link, date = job
            print(f"🔹 {title} | {company}")
            print(f"   📍 {location}")
            print(f"   🔗 {link}")
            print(f"   📅 {date}\n")
        return

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logger = logging.getLogger(__name__)

    # Silence httpx logger
    logging.getLogger("httpx").setLevel(logging.WARNING)

    parsers = [
        GoogleParser(),
        GoogleDeepMindParser(),
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
        CiscoParser(),
        AnthropicParser(),
        DatadogParser(),
    ]

    logger.info("🌍 Starting shared browser session...")
    driver = None
    try:
        driver = get_driver(headless=True)
        new_jobs = crawl(parsers, keywords, exclude, driver=driver)
    except Exception as e:
        logger.error(f"❌ Error initializing or using driver: {e}")
        # potential fallback or raise
        new_jobs = [] 
    finally:
        if driver:
            logger.info("🛑 Closing shared browser session...")
            driver.quit()

    if new_jobs:
        logger.info(f"📨 Sending {len(new_jobs)} new jobs to Telegram…")
        send_new_jobs(new_jobs)
    else:
        logger.info("✔ No new jobs today.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Job tracker script")
    parser.add_argument("--keywords","-k",
                        nargs="+",  # Allows passing keywords splited by space
                        help="Keyword list to search",
                        default=["security research",
                                 "research intern",
                                 "internship",
                                 "PhD",
                                 "cybercrime"]
                        )
    parser.add_argument("--exclude", "-e",
                        nargs="+",
                        help="Keywords to exclude from results",
                        default=["Senior",
                                 "Sr.",
                                 "Director",
                                 "Manager",
                                 "Coordinator"])
    parser.add_argument("--verbose", "-v",
                        action="store_true",
                        help="Enable verbose logging")
    parser.add_argument("--list", "-l",
                        action="store_true",
                        help="List last 10 jobs found")
    args = parser.parse_args()
    main(args.keywords, args.exclude, args.verbose, args.list)
