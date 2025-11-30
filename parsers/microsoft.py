from .base_parser import BaseParser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import html


class MicrosoftParser(BaseParser):
    name = "Microsoft"

    def build_urls(self, keywords):
        urls = []
        base = "https://apply.careers.microsoft.com/careers?domain=microsoft.com&start=0&pid=1970393556621058&sort_by=match&query="
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
        job_cards = soup.select('[data-test-id="job-listing"]')

        for card in job_cards:
            try:
                title_elem = card.select_one(".title-1aNJK")
                title = title_elem.get_text(strip=True) if title_elem else "N/A"

                # Location in a list or simple paragraph
                location = self.parse_locations(card)

                # Link
                link = self.parse_link(card)

                jobs_data.append({
                    "title": title,
                    "company": "Microsoft",
                    "location": location,
                    "link": link
                })
            except AttributeError:
                continue

        return jobs_data


    @staticmethod
    def parse_locations(job_card):
        country_elem = job_card.select_one('.fieldValue-3kEar')
        if country_elem:
            full_country = country_elem.get_text(strip=True)

        return full_country or "N/A"

    @staticmethod
    def parse_link(job_card):
        """
        Extracts the absolute URL of the job offer.
        """
        a = job_card.find("a", href=True)
        if not a:
            return "N/A"

        href = a["href"]
        # Convert relative → absolute
        if href.startswith("/"):
            return "https://careers.microsoft.com" + href
        return href
