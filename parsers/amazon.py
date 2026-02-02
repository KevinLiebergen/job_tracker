from .base_parser import BaseParser
from src.driver_factory import get_driver
from bs4 import BeautifulSoup
import time
import html


class AmazonParser(BaseParser):
    name = "Amazon"

    def build_urls(self, keywords):
        urls = []
        base = "https://www.amazon.jobs/es/search/?base_query="
        for kw in keywords:
            urls.append(base + kw.replace(" ", "+"))
        return urls

    def parse(self, url: str, keywords) -> list:

        driver = get_driver(headless=True)

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

        # In Amazon, positions used to be under divs with class 'job-tile'
        job_cards = soup.find_all('div', class_='job-tile')

        for card in job_cards:
            try:
                title = card.find('h3', class_='job-title').text.strip()

                # Location in a list or simple paragraph
                location = self.parse_locations(card)

                # Link
                link = self.parse_link(card)

                jobs_data.append({
                    "title": title,
                    "company": self.name,
                    "location": location,
                    "link": link
                })
            except AttributeError:
                print(f"Error parsing job: {card}")

        return jobs_data


    @staticmethod
    def parse_locations(card):
        # 1. Get the list of <li> tags inside the location block
        location_block = card.select_one(".location-and-id ul")

        if not location_block:
            return "N/A"

        li_tags = location_block.find_all("li", recursive=False)

        # First <li> is always the main location
        main_location = li_tags[0].get_text(strip=True)

        # 2. Check if there's a popover with extra locations
        button = card.select_one("button.popover-button")

        extra_locations = []
        if button:
            raw_html = button.get("data-content", "")
            decoded_html = html.unescape(raw_html)  # decode &lt;...&gt;
            soup_extra = BeautifulSoup(decoded_html, "html.parser")

            extra_locations = [li.get_text(strip=True) for li in soup_extra.find_all("li")]

        # Merge results
        if extra_locations:
            all_locations = [main_location] + extra_locations
            return ", ".join(all_locations)

        return main_location

    @staticmethod
    def parse_link(card):
        a = card.select_one("a.job-link")
        if not a:
            return "N/A"

        relative_url = a.get("href")
        if not relative_url:
            return "N/A"

        base_url = "https://www.amazon.jobs"
        full_url = base_url + relative_url

        return full_url
