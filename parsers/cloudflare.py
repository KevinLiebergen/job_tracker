from .base_parser import BaseParser
import requests

class CloudflareParser(BaseParser):
    name = "Cloudflare"
    # Defined inside the class
    SPECIFIC_KEYWORDS = [
        "Research Engineer Intern",
    ]

    def build_urls(self, keywords):
        return ["https://boards-api.greenhouse.io/v1/boards/cloudflare/jobs/"]

    def parse(self, url: str, base_keywords: list, driver=None) -> list:

        response = requests.get(url)
        all_jobs = response.json().get('jobs', [])
        keywords = list(set(base_keywords + self.SPECIFIC_KEYWORDS))

        filtered_jobs = self.filter_jobs(all_jobs, keywords)

        # Send HTML to BeautifulSoup
        jobs = self.parse_jobs(filtered_jobs)

        return jobs


    @staticmethod
    def filter_jobs(jobs, keywords):
        filtered = []
        for job in jobs:
            title = job.get('title', '').lower()

            for kw in keywords:
                kw_lower = kw.lower()
                if kw_lower in title:
                    filtered.append(job)
                    break
        return filtered

    def parse_jobs(self, filtered_jobs) -> list:
        jobs = []



        for job in filtered_jobs:
            title = job.get('title')
            link = job.get('absolute_url')
            location = ' or '.join(job.get('metadata')[1].get('value'))

            # Append to list
            jobs.append({
                "title": title,
                "company": self.name,
                "location": location,
                "link": link
            })

        return jobs