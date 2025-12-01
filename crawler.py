import hashlib
from parsers import google, amazon, cloudflare
from database import job_exists, save_job
import time

# Dictionary to access parser by name
#PARSERS = {
#    "google": google.parse,
#    "amazon": amazon.parse,
#    "cloudflare": cloudflare.parse,
#}

def hash_job(title, link):
    return hashlib.sha256((title + link).encode()).hexdigest()


def build_urls(url_config, keywords=None):
    urls_to_crawl = []
    for config in url_config:
        base = config["base_url"]
        parser = config.get("parser", "generic")
        param = config.get("param_name", "q")

        if keywords:
            for kw in keywords:
                url = f"{base}?{param}={kw}"
                urls_to_crawl.append((url, parser))
        else:
            urls_to_crawl.append((base, parser))

    return urls_to_crawl


def crawl(parsers, keywords):
    new_jobs = []
    jobs_extended = []

    for parser_obj in parsers:
        print(f"\n📌 Running parser: {parser_obj.name}")

        # Each parser knows how to build the correct URL(s)
        urls = parser_obj.build_urls(keywords)
        print(f"  → URLs to visit: {urls}")

        for url in urls:
            print(f"    → Visiting: {url}")

            # Parse the HTML
            try:
                jobs = parser_obj.parse(url, keywords)
                jobs_extended.extend(jobs)

            except Exception as e:
                print(f"    ❌ Parsing error in {parser_obj.name}: {e}")
                continue

            print(f"    → Parsed {len(jobs)} jobs")

        for job in jobs_extended:
            job_id = hash_job(job["title"], job["link"])

            if not job_exists(job_id):
                save_job(job_id, job)
                new_jobs.append(job)

    return new_jobs
