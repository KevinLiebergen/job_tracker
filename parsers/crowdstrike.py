from .base_parser import BaseParser
from src.driver_factory import get_driver
from bs4 import BeautifulSoup
import time


class CrowdstrikeParser(BaseParser):
    name = "Crowdstrike"

    def build_urls(self, keywords):
        urls = []
        base = "https://crowdstrike.wd5.myworkdayjobs.com/crowdstrikecareers?q="
        for kw in keywords:
            urls.append(base + kw.replace(" ", "+"))
        return urls

    def parse(self, url: str, keywords, driver=None, should_quit=False) -> list:
        if driver:
            self._driver = driver
        
        driver = self.driver

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

        jobs_data = []

        title_links = soup.find_all('a', attrs={'data-automation-id': 'jobTitle'})

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
