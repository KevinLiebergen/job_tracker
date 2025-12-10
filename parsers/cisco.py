from .base_parser import BaseParser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup, SoupStrainer
import time
import json
import re


class CiscoParser(BaseParser):
    name = "Cisco"

    def build_urls(self, keywords):
        urls = []
        base = "https://careers.cisco.com/global/en/search-results?keywords="
        for kw in keywords:
            urls.append(base + kw.replace(" ", "+"))
        return urls

    def parse(self, url: str, keywords) -> list:

        only_scripts = SoupStrainer("script")

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Execution without GUI

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        driver.get(url)

        # Wait for JavaScript loads everything
        time.sleep(5)

        # Extract HTML
        rendered_html = driver.page_source
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
                    link = job.get('applyUrl', 'N/A')

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