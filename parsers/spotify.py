from .base_parser import BaseParser
from src.driver_factory import get_driver
from bs4 import BeautifulSoup
import time
import html


class SpotifyParser(BaseParser):
    name = "Spotify"

    def build_urls(self, keywords):
        urls = []
        base = "https://www.lifeatspotify.com/jobs?q="
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
        job_cards = soup.find_all('div', class_='entry_container__eT9IU')

        for card in job_cards:
            try:
                title = self.parse_title(card)

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
                continue

        return jobs_data

    @staticmethod
    def parse_title(card):
        # --- Extract Title ---
        # Title is in an <h2> tag with class "entry_title__Q0z3u"
        title_tag = card.find('h2', class_='entry_title__Q0z3u')
        title = title_tag.get_text(strip=True) if title_tag else "N/A"
        return title


    @staticmethod
    def parse_locations(card):
        # --- Extract Location ---
        # Locations appear twice (mobile/desktop). We target the desktop version
        # which has the class "is-hidden-mobile" to avoid duplicates.
        location_tag = card.find('p', class_='is-hidden-mobile')
        if location_tag:
            location = location_tag.get_text(strip=True)
        else:
            # Fallback if the desktop tag isn't found
            location = "N/A"
        return location

    @staticmethod
    def parse_link(card):
        # --- Extract Link ---
        # The URL isn't in an href. It's in the 'data-info' attribute (the slug).
        # We must prepend the base URL manually.
        slug = card.get('data-info')
        if slug:
            link = f"https://www.lifeatspotify.com/jobs/{slug}"
        else:
            link = "N/A"
        return link
