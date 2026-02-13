from .base_parser import BaseParser
from src.driver_factory import get_driver
from bs4 import BeautifulSoup, SoupStrainer
import time
import json
import re


class CiscoParser(BaseParser):
    name = "Cisco"
    SPECIFIC_KEYWORDS = ["Talos"]

    def build_urls(self, keywords):
        # Merge with specific keywords
        combined_keywords = list(set(keywords + self.SPECIFIC_KEYWORDS))
        urls = []
        base = "https://careers.cisco.com/global/en/search-results?keywords="
        for kw in combined_keywords:
            urls.append(base + kw.replace(" ", "+"))
        return urls

    def parse(self, url: str, keywords, driver=None) -> list:

        only_scripts = SoupStrainer("script")

        driver = self.driver # get_driver(headless=True)

        driver.get(url)

        # Check for blocking
        from src.utils import check_page_status
        from src.notifier import send_blocking_alert
        blocking_reason = check_page_status(driver, url)
        if blocking_reason:
            send_blocking_alert(self.name, url, blocking_reason)

        # Wait for JavaScript loads everything
        time.sleep(5)

        # Extract HTML
        rendered_html = driver.page_source
        if should_quit:
            driver.quit()

        # Send HTML to BeautifulSoup
        soup = BeautifulSoup(rendered_html, 'html.parser', parse_only=only_scripts)

        jobs = self.parse_jobs(soup)

        return jobs


    def parse_jobs(self, soup) -> list:
        jobs = []

        # Now 'soup' only contains <script> tags, not the whole page
        target_script = None

        # Iterate through the scripts to find the one with our data
        for script in soup:
            if script.string and 'phApp.ddo =' in script.string:
                target_script = script.string
                break

        if not target_script:
            print("Script not found.")
            return []

        # Extract JSON using Regex
        pattern = r'phApp\.ddo\s*=\s*(\{.*?\});'
        match = re.search(pattern, target_script, re.DOTALL)

        if match:
            try:
                data = json.loads(match.group(1))
                parsed_jobs = data.get('eagerLoadRefineSearch', {}).get('data', {}).get('jobs', [])
                for job in parsed_jobs:
                    title = job.get('title', 'N/A')
                    location = job.get('location', 'N/A')
                    apply_link = job.get('applyUrl', 'N/A')
                    link = apply_link.removesuffix('/apply')

                    jobs.append({
                        "title": title,
                        "company": self.name,
                        "location": location,
                        "link": link
                    })
                return jobs
            except json.JSONDecodeError:
                return []
        return []
