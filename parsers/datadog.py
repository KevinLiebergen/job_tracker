from .base_parser import BaseParser
from src.driver_factory import get_driver
from bs4 import BeautifulSoup
import time

class DatadogParser(BaseParser):
    name = "Datadog"
    SPECIFIC_KEYWORDS = []

    def build_urls(self, keywords):
        combined = list(set(keywords + self.SPECIFIC_KEYWORDS))
        return [f"https://careers.datadoghq.com/all-jobs/?s={k.replace(' ', '+')}" for k in combined]

    def parse(self, url: str, base_keywords: list, driver=None, should_quit=False) -> list:
        # Selenium setup
        if driver:
            self._driver = driver
        
        driver = self.driver

        try:
            driver.get(url)
            
            # Check for blocking
            from src.utils import check_page_status
            from src.notifier import send_blocking_alert
            blocking_reason = check_page_status(driver, url)
            if blocking_reason:
                send_blocking_alert(self.name, url, blocking_reason)

            # Wait for hits to load
            try:
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.common.by import By
                # Wait for at least one job card or specific container
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ais-Hits-item"))
                )
            except:
                # Might be 0 results, which is fine
                pass
            
            # Additional small sleep to ensure rendering is stable
            time.sleep(2)
            
            html_content = driver.page_source
        finally:
            if should_quit:
                driver.quit()

        soup = BeautifulSoup(html_content, 'html.parser')
        jobs = self.parse_jobs(soup)
        return jobs

    def parse_jobs(self, soup) -> list:
        jobs = []
        hits = soup.select('.ais-Hits-item')
        for hit in hits:
            # Title
            title_tag = hit.select_one('.job-title')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            
            # Link
            a_tag = hit.select_one('a')
            if a_tag and a_tag.get('href'):
                link = "https://careers.datadoghq.com" + a_tag['href']
            else:
                link = "N/A"
            
            # Location
            location = "N/A"
            
            # Check for direct location
            direct_loc_tag = hit.select_one('.job-card-location p')
            if direct_loc_tag:
                text = direct_loc_tag.get_text(strip=True)
                if text != "Locations":
                    location = text

            # If location is still N/A (or was "Locations"), try 'more locations' result
            if location == "N/A":
                more_loc = hit.select_one('.more-locations-result')
                if more_loc:
                     location = more_loc.get_text(strip=True)

            jobs.append({
                "title": title,
                "company": self.name,
                "location": location,
                "link": link
            })
        
        return jobs
