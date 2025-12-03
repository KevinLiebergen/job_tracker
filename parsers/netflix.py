from .base_parser import BaseParser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import html
import json


class NetflixParser(BaseParser):
    name = "Netflix"

    def build_urls(self, keywords):
        urls = []
        base = "https://explore.jobs.netflix.net/careers?query="
        for kw in keywords:
            urls.append(base + kw.replace(" ", "+"))
        return urls

    def parse(self, url: str, keywords) -> list:

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
        soup = BeautifulSoup(rendered_html, 'html.parser')

        jobs = self.parse_jobs(soup)

        return jobs


    def parse_jobs(self, soup) -> list:

        jobs_data = []

        data_container = soup.find('code', id='smartApplyData')
        json_text = data_container.get_text()
        data = json.loads(json_text)

        # The JSON structure is: root -> positions -> [list of jobs]
        jobs_list = data.get('positions', [])

        for job in jobs_list:
            try:
                title = job.get('name', 'N/A')

                location = job.get('location', 'N/A')

                # The URL is explicitly available in the JSON
                link = job.get('canonicalPositionUrl', 'N/A')

                jobs_data.append({
                    "title": title,
                    "company": self.name,
                    "location": location,
                    "link": link
                })
            except AttributeError:
                print(f"Error parsing job: {job}")
                continue

        return jobs_data
