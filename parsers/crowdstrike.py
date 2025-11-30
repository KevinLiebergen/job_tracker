from .base_parser import BaseParser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import html


class CrowdstrikeParser(BaseParser):
    name = "Crowdstrike"

    def build_urls(self, keywords):
        urls = []
        base = "https://crowdstrike.wd5.myworkdayjobs.com/crowdstrikecareers?q="
        for kw in keywords:
            urls.append(base + kw.replace(" ", "+"))
        return urls

    def parse(self, url: str, keywords) -> list:

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Execution without GUI

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        driver.get(url)

        # Wait for JavaScript loads everything
        time.sleep(10)

        # Extract HTML
        rendered_html = driver.page_source
        driver.quit()

        # Send HTML to BeautifulSoup
        soup = BeautifulSoup(rendered_html, 'html.parser')

        jobs = self.parse_jobs(soup)

        return jobs


    def parse_jobs(self, soup) -> list:

        jobs_data = []

        title_links = soup.find_all('a', attrs={'data-automation-id': 'jobTitle'})

        print(f"Found {len(title_links)} job cards.\n")

        for title_tag in title_links:
            # We can extract most data relative to the title tag
            # or find the parent <li> container to scope our search
            card = title_tag.find_parent('li')

            if not card:
                continue

            # --- Title ---
            title = title_tag.get_text(strip=True)

            # --- Link ---
            # Workday links are relative, so we prepend the base domain found in the file
            relative_link = title_tag.get('href')
            link = f"https://crowdstrike.wd5.myworkdayjobs.com{relative_link}"

            location = self.parse_locations(title_tag)

            jobs_data.append({
                "title": title,
                "company": self.name,
                "location": location,
                "link": link,
            })

        return jobs_data


    @staticmethod
    def parse_locations(tag):
        # --- Location ---
        # Logic: Split by "/job/" and take the next segment
        try:
            location = tag.get('href').split('/job/')[1].split('/')[0]
            return location
        except IndexError:
            return "N/A"
