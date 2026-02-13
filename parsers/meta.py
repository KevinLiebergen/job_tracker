from .base_parser import BaseParser
from src.driver_factory import get_driver
from bs4 import BeautifulSoup
import time


class MetaParser(BaseParser):
    name = "Meta"

    def build_urls(self, keywords):
        urls = []
        base = "https://www.metacareers.com/jobsearch?q="
        for kw in keywords:
            urls.append(base + kw.replace(" ", "+"))
        return urls

    def parse(self, url: str, keywords) -> list:
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
        soup = BeautifulSoup(rendered_html, 'html.parser')

        jobs = self.parse_jobs(soup)

        return jobs

    def parse_jobs(self, soup) -> list:
        jobs = []

        # Meta uses relative links with the structure “/jobs/<numeric_id>”
        # We search for all <a> tags that have an href that matches this pattern.
        job_cards = soup.find_all('a', href=True)

        for card in job_cards:
            link_href = card['href']

            # We only filter links that are job offers (they start with /jobs/ and are followed by numbers).
            # Example: /jobs/733601195817272
            if link_href.startswith('/jobs/') and link_href.split('/')[-1].isdigit():

                # 1. Title
                # The title is usually in an h3 or h4 within the link.
                title = self.parse_title(card)

                # 2. Link
                # We build the absolute link
                link = f"https://www.metacareers.com{link_href}"

                # 4. Location
                location = self.parse_location(card, title)

                jobs.append({
                    "title": title,
                    "company": self.name,
                    "location": location,
                    "link": link
                })

        return jobs



    @staticmethod
    def parse_title(card):
        title_tag = card.find(['h3', 'h4'])
        if not title_tag:
            return None
        title = title_tag.get_text(strip=True)

        return title

    @staticmethod
    def parse_location(card, title):
        # Location is more difficult because CSS classes are random (e.g., “x16g9bbj”).
        # Strategy: Extract all text from the card by separating it with pipes “|”
        # The format is usually: “Title | Location | · | Category”
        card_text = card.get_text(separator='|', strip=True)
        text_parts = card_text.split('|')

        location = "N/A"
        # Normally, the location is the second visible element, right after the title.
        # Sometimes there is an invisible “Bookmark” button in between, so we filter a little.
        for part in text_parts:
            if part != title and part not in ['·', '⋅', 'Bookmark']:
                location = part
                break

        # Limpieza extra por si captura algo que no es
        if location == "Job Search" or location == "Jobs":
            location = "N/A"
        return location

    @staticmethod
    def parse_link(card):
        # The anchor tag usually has class 'WpHeLc'
        link = "N/A"
        link_tag = card.find('a', class_='WpHeLc')
        if link_tag and link_tag.get('href'):
            # Google career links are relative in the HTML
            relative_link = link_tag['href']
            link = f"https://www.google.com/about/careers/applications/{relative_link}"
        return link
