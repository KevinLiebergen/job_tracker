from .base_parser import BaseParser
import requests
from config.settings import HEADERS
from bs4 import BeautifulSoup


class PaloAltoParser(BaseParser):
    name = "PaloAlto"

    def build_urls(self, keywords):
        urls = []
        base = "https://jobs.paloaltonetworks.com/en/search-jobs/"
        for kw in keywords:
            urls.append(base + kw.replace(" ", "+"))
        return urls

    def parse(self, url: str, keywords, driver=None, should_quit=False) -> list:
        # List to hold the extracted job data
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        jobs = self.parse_jobs(soup)

        return jobs

    def parse_jobs(self, soup) -> list:
        jobs = []

        # The jobs are listed in <li> elements with the class 'section29__search-results-li'
        job_cards = soup.find_all('li', class_='section29__search-results-li')

        for card in job_cards:
            # Title is usually in an h3 tag with class 'QJPWVe'
            title_tag = card.find('h2', class_='section29__search-results-job-title')
            title = title_tag.get_text(strip=True) if title_tag else "N/A"

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
    def parse_location(card):
        # Located in a <span> with class 'section29__result-location'
        location_tag = card.find('span', class_='section29__result-location')
        location = location_tag.get_text(strip=True) if location_tag else "N/A"
        return location

    @staticmethod
    def parse_link(card):
        link_tag = card.find('a', class_='section29__search-results-link')
        if link_tag and link_tag.get('href'):
            relative_link = link_tag['href']
            # Prepend the base domain found in the file's meta tags
            link = f"https://jobs.paloaltonetworks.com{relative_link}"
        else:
            link = "N/A"
        return link
