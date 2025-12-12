from .base_parser import BaseParser
import requests
from bs4 import BeautifulSoup


class GoogleDeepMindParser(BaseParser):
    name = "Google DeepMind"


    def build_urls(self, keywords):
        urls = []
        base = "https://job-boards.greenhouse.io/deepmind?keyword="
        for kw in keywords:
            urls.append(base + kw.replace(" ", "+"))
        return urls

    def parse(self, url: str, keywords: list) -> list:

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")


        # Send HTML to BeautifulSoup
        jobs = self.parse_jobs(soup)

        return jobs


    def parse_jobs(self, soup) -> list:
        jobs_data = []

        # Greenhouse job boards typically list jobs in divs with class 'job-post'
        # Each 'job-post' contains the title link and location.
        job_openings = soup.find_all('tr', class_='job-post')

        for opening in job_openings:
            # 1. Link & Title
            # The title is inside an <a> tag
            link_tag = opening.find('a')

            if not link_tag:
                continue

            title = self.parse_title(link_tag)
            location = self.parse_location(link_tag)
            link = self.parse_link(link_tag)

            jobs_data.append({
                "title": title,
                "company": self.name,
                "location": location,
                "link": link
            })

        return jobs_data

    @staticmethod
    def parse_title(link_tag):
        title_tag = link_tag.find('p', class_='body--medium')
        # Remove the "New" badge span so it doesn't get included in the text
        if title_tag:
            badge = title_tag.find('span')
            if badge:
                badge.decompose()  # Deletes the tag from the tree

            title = title_tag.get_text(strip=True)
        else:
            title = "N/A"
        return title

    @staticmethod
    def parse_location(link_tag):
        # --- 2. Extract Location ---
        # Find the second paragraph tag
        location_tag = link_tag.find('p', class_='body--metadata')

        if location_tag:
            location = location_tag.get_text(strip=True)
        else:
            location = "N/A"

        return location


    @staticmethod
    def parse_link(link_tag):
        # Greenhouse links are usually relative (e.g. "/jobs/12345")
        relative_link = link_tag.get('href')
        if relative_link.startswith('http'):
            link = relative_link
        else:
            # Prepend the base domain if it's a relative path
            link = f"https://boards.greenhouse.io{relative_link}"

        return link
