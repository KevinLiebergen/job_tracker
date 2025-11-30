from .base_parser import BaseParser
import requests
from config.settings import HEADERS
from bs4 import BeautifulSoup


class GoogleParser(BaseParser):
    name = "Google"

    def build_urls(self, keywords):
        urls = []
        base = "https://careers.google.com/jobs/results/?q="
        for kw in keywords:
            urls.append(base + kw.replace(" ", "+"))
        return urls

    def parse(self, url: str, keywords) -> list:
        # List to hold the extracted job data
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        jobs = self.parse_jobs(soup)

        return jobs

    def parse_jobs(self, soup) -> list:
        jobs = []

        # Google Careers typically lists jobs in <li> items with class 'lLd3Je'
        # or container divs. Based on the file provided, we look for the specific list items.
        job_cards = soup.find_all('li', class_='lLd3Je')

        for card in job_cards:
            # Title
            # Title is usually in an h3 tag with class 'QJPWVe'
            title_tag = card.find('h3', class_='QJPWVe')
            title = title_tag.text.strip() if title_tag else "N/A"

            # Location
            location = self.parse_location(card)

            # Link
            link = self.parse_link(card)

            # Append to list
            jobs.append({
                "title": title,
                "company": self.name,
                "location": location,
                "link": link
            })

        return jobs


    @staticmethod
    def parse_company(card, title):
        # Company name often appears in a specific div 'op1BBf' alongside an icon.
        # We search for the text directly or specific span classes.
        # The file shows structure like: <div class="op1BBf">...<span>Google</span>
        company = "Google"  # Default, as it's the Google Careers site
        company_container = card.find('div', class_='op1BBf')
        if company_container:
            # Try to find the span that contains the company name (often near 'corporate_fare' icon)
            # This finds the text of the parent or specific span
            text_content = company_container.get_text(separator="|")
            if "Google" in text_content:
                company = "Google"
            elif "Mandiant" in title:  # Mandiant is a common Google subsidiary in these listings
                company = "Mandiant (Google Cloud)"

        return company


    @staticmethod
    def parse_location(card):
        # Locations are often in a span with class 'r0wTof' inside a container 'pwO9Dc'
        location = "N/A"
        loc_container = card.find('span', class_='pwO9Dc')
        if loc_container:
            # Sometimes there are multiple locations (e.g., "New York; +1 more")
            # We extract all text within this container
            location = " ".join([t for t in loc_container.stripped_strings if t != "place"])

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
