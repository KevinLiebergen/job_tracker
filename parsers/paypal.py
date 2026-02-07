from .base_parser import BaseParser
from src.driver_factory import get_driver
from bs4 import BeautifulSoup
import time
import html


class PayPalParser(BaseParser):
    name = "PayPal"

    def build_urls(self, keywords):
        urls = []
        base = "https://paypal.eightfold.ai/careers?&start=0&pid=274916842621&sort_by=match&query="
        for kw in keywords:
            urls.append(base + kw.replace(" ", "+"))
        return urls

    def parse(self, url: str, keywords, driver=None) -> list:
        if not driver:
            driver = get_driver(headless=True)
            should_quit = True
        else:
            should_quit = False

        driver.get(url)

        # Wait for JavaScript loads everything
        time.sleep(5)

        # Extract HTML
        rendered_html = driver.page_source
        if should_quit:
            driver.quit()

        # Send HTML to BeautifulSoup
        soup = BeautifulSoup(rendered_html, 'html.parser')

        jobs = self.parse_jobs(soup)

        return jobs


    def parse_jobs(self, soup) -> list:
        jobs = []

        # Google Careers typically lists jobs in <li> items with class 'lLd3Je'
        # or container divs. Based on the file provided, we look for the specific list items.
        job_cards = soup.find_all('div', attrs={'data-test-id': 'job-listing'})

        for card in job_cards:
            # 1. Link
            # The main link is the container <a> tag.
            link_tag = card.find('a')
            if not link_tag:
                continue

            relative_link = link_tag.get('href')
            # We build the absolute URL (assuming the Eightfold/PayPal domain)
            link = f"https://paypal.eightfold.ai{relative_link}"

            # 2. Title
            # The title is inside a div with a specific class.
            # In your file it is “title-1aNJK,” but to be more flexible we look for the first div with meaningful text inside the link.
            # Or we use the specific class if we want precision:
            title_tag = card.find('div', class_='title-1aNJK')
            title = title_tag.get_text(strip=True) if title_tag else "N/A"

            # 3. Location
            location = self.parse_location(card)

            # Append to list
            jobs.append({
                "title": title,
                "company": self.name,
                "location": location,
                "link": link
            })

        return jobs


    @staticmethod
    def parse_location(card):
        # The location is in a div with class “fieldValue-3kEar”.
        # Sometimes there are several (e.g., Department), but the location is usually the first one or has a map icon.
        # In your HTML, the first “fieldValue” is the location.
        field_values = card.find_all('div', class_='fieldValue-3kEar')
        location = "N/A"
        if field_values:
            location = field_values[0].get_text(strip=True)
        return location
