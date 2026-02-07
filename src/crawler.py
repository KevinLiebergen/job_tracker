import hashlib
import logging
from .database import job_exists, save_job

logger = logging.getLogger(__name__)

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


def crawl(parsers, keywords, exclude=None, driver=None):
    new_jobs = []
    jobs_extended = []

    for parser_obj in parsers:
        logger.info(f"📌 Running parser: {parser_obj.name}")

        # Each parser knows how to build the correct URL(s)
        urls = parser_obj.build_urls(keywords)
        logger.info(f"  → URLs to visit: {urls}")

        for url in urls:
            logger.info(f"    → Visiting: {url}")

            # Parse the HTML
            try:
                jobs = parser_obj.parse(url, keywords, driver=driver)
                if exclude:
                    jobs = [job for job in jobs if not any(ex.lower() in job["title"].lower() for ex in exclude)]
                
                for job in jobs:
                    logger.debug(f"      Job found: {job['title']} ({job['link']})")

                jobs_extended.extend(jobs)

            except Exception as e:
                logger.error(f"    ❌ Parsing error in {parser_obj.name}: {e}")
                from .notifier import send_error
                send_error(parser_obj.name, str(e))
                continue

            logger.info(f"    → Parsed {len(jobs)} jobs\n")

        for job in jobs_extended:
            job_id = hash_job(job["title"], job["link"])

            if not job_exists(job_id):
                save_job(job_id, job)
                new_jobs.append(job)

    return new_jobs
