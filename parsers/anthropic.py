from .base_parser import BaseParser
import requests

class AnthropicParser(BaseParser):
    name = "Anthropic"
    SPECIFIC_KEYWORDS = ["security"]

    def build_urls(self, keywords):
        return ["https://boards-api.greenhouse.io/v1/boards/anthropic/jobs/"]

    def parse(self, url: str, base_keywords: list) -> list:
        response = requests.get(url)
        all_jobs = response.json().get('jobs', [])

        # Merge with specific keywords (pattern adoption)
        keywords = list(set(base_keywords + self.SPECIFIC_KEYWORDS))
        
        filtered_jobs = self.filter_jobs(all_jobs, keywords)

        jobs = self.parse_jobs(filtered_jobs)
        return jobs

    @staticmethod
    def filter_jobs(jobs, keywords):
        filtered = []
        for job in jobs:
            title = job.get('title', '').lower()
            for kw in keywords:
                if kw.lower() in title:
                    filtered.append(job)
                    break
        return filtered

    def parse_jobs(self, filtered_jobs) -> list:
        jobs = []
        for job in filtered_jobs:
            title = job.get('title')
            link = job.get('absolute_url')
            location = job.get('location', {}).get('name', 'N/A')

            jobs.append({
                "title": title,
                "company": self.name,
                "location": location,
                "link": link
            })
        return jobs
