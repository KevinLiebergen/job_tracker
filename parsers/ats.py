"""Generic parsers for companies hosted on a standard ATS.

Instead of one hand-written parser file per company, every company that publishes
its board through a known applicant tracking system is a single entry in
config/companies.py. The classes below turn a board token into a JSON endpoint
and normalise the response into the usual job dict.
"""
from .base_parser import BaseParser
from config.companies import COMPANIES
from config.settings import HEADERS
import logging
import requests
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

TIMEOUT = 20


class AtsParser(BaseParser):
    """Base for API-backed boards. Subclasses provide api_url() and extract()."""

    ats = "ats"

    def __init__(self, name, token, extra=None, driver=None):
        super().__init__(driver)
        self.name = name
        self.token = token
        self.extra = extra or {}

    def build_urls(self, keywords):
        # The board API returns every posting at once, so keywords are applied
        # after fetching rather than as a query parameter.
        return [self.api_url()]

    def api_url(self):
        raise NotImplementedError

    def fetch(self, url, keywords=None):
        # Most boards return every posting in one response, so keywords are unused
        # here and applied by parse(). WorkdayParser overrides this.
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()

    def extract(self, payload):
        """Return a list of (title, location, link) tuples."""
        raise NotImplementedError

    def parse(self, url: str, keywords, driver=None, should_quit=False) -> list:
        payload = self.fetch(url, keywords)

        jobs = []
        for title, location, link in self.extract(payload):
            if not title or not link:
                continue
            if not self.matches(title, keywords):
                continue

            jobs.append({
                "title": title,
                "company": self.name,
                "location": location or "N/A",
                "link": link,
            })

        return jobs

    @staticmethod
    def matches(title, keywords):
        if not keywords:
            return True
        title = title.lower()
        return any(kw.lower() in title for kw in keywords)

    @staticmethod
    def strip_query(link):
        # Query parameters make the same posting hash differently on every run.
        return link.split("?")[0] if link else link

    @staticmethod
    def join_location(*parts):
        return ", ".join(p for p in parts if p) or "N/A"


class GreenhouseParser(AtsParser):
    ats = "greenhouse"

    def api_url(self):
        return f"https://boards-api.greenhouse.io/v1/boards/{self.token}/jobs/"

    def extract(self, payload):
        return [(job.get("title"),
                 (job.get("location") or {}).get("name"),
                 self.strip_query(job.get("absolute_url")))
                for job in payload.get("jobs", [])]


class LeverParser(AtsParser):
    ats = "lever"

    def api_url(self):
        return f"https://api.lever.co/v0/postings/{self.token}?mode=json"

    def extract(self, payload):
        jobs = []
        for job in payload:
            categories = job.get("categories") or {}
            jobs.append((job.get("text"),
                         categories.get("location"),
                         self.strip_query(job.get("hostedUrl"))))
        return jobs


class AshbyParser(AtsParser):
    ats = "ashby"

    def api_url(self):
        return f"https://api.ashbyhq.com/posting-api/job-board/{self.token}"

    def extract(self, payload):
        return [(job.get("title"), job.get("location"), self.strip_query(job.get("jobUrl")))
                for job in payload.get("jobs", [])]


class SmartRecruitersParser(AtsParser):
    ats = "smartrecruiters"

    def api_url(self):
        return f"https://api.smartrecruiters.com/v1/companies/{self.token}/postings?limit=100"

    def extract(self, payload):
        jobs = []
        for job in payload.get("content", []):
            location = job.get("location") or {}
            jobs.append((job.get("name"),
                         self.join_location(location.get("city"), location.get("country")),
                         f"https://jobs.smartrecruiters.com/{self.token}/{job.get('id')}"))
        return jobs


class WorkableParser(AtsParser):
    ats = "workable"

    def api_url(self):
        return f"https://apply.workable.com/api/v1/widget/accounts/{self.token}?details=true"

    def extract(self, payload):
        jobs = []
        for job in payload.get("jobs", []):
            jobs.append((job.get("title"),
                         self.join_location(job.get("city"), job.get("country")),
                         self.strip_query(job.get("url") or job.get("shortlink"))))
        return jobs


class RecruiteeParser(AtsParser):
    ats = "recruitee"

    def api_url(self):
        return f"https://{self.token}.recruitee.com/api/offers/"

    def extract(self, payload):
        jobs = []
        for job in payload.get("offers", []):
            jobs.append((job.get("title"),
                         job.get("location") or self.join_location(job.get("city"),
                                                                   job.get("country")),
                         self.strip_query(job.get("careers_url") or job.get("careers_apply_url"))))
        return jobs


class PersonioParser(AtsParser):
    """Personio only exposes an XML feed, no JSON API."""

    ats = "personio"

    def api_url(self):
        return f"https://{self.token}.jobs.personio.de/xml"

    def fetch(self, url):
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return ET.fromstring(response.content)

    def extract(self, payload):
        jobs = []
        for position in payload.iter("position"):
            def text(tag):
                node = position.find(tag)
                return node.text.strip() if node is not None and node.text else None

            job_id = text("id")
            link = text("jobDescriptionUrl") or (
                f"https://{self.token}.jobs.personio.de/job/{job_id}" if job_id else None)
            jobs.append((text("name"), text("office"), self.strip_query(link)))
        return jobs


class ComeetParser(AtsParser):
    """Comeet needs the company id alongside the board token.

    Both are embedded in the careers page: the id looks like '91.001' and the token is
    a long hex string on the widget's script tag or data-uid attribute.
    """

    ats = "comeet"

    def api_url(self):
        return (f"https://www.comeet.co/careers-api/2.0/company/{self.extra.get('company')}"
                f"/positions?token={self.token}&details=true")

    def extract(self, payload):
        jobs = []
        for job in payload:
            location = job.get("location") or {}
            jobs.append((job.get("name"),
                         location.get("name") or self.join_location(location.get("city"),
                                                                    location.get("country")),
                         self.strip_query(job.get("url_comeet_hosted_page")
                                          or job.get("url_active_page"))))
        return jobs


class WorkdayParser(AtsParser):
    """Workday's job list is a POST endpoint, paginated 20 at a time."""

    ats = "workday"
    PAGE_SIZE = 20
    MAX_PAGES = 10

    @property
    def host(self):
        return f"https://{self.token}.{self.extra.get('wd', 'wd1')}.myworkdayjobs.com"

    @property
    def site(self):
        return self.extra.get("site")

    def api_url(self):
        return f"{self.host}/wday/cxs/{self.token}/{self.site}/jobs"

    def fetch(self, url, keywords=None):
        """Search once per keyword.

        Workday hands out 20 postings at a time, and some tenants here are whole
        corporate boards with a thousand openings. Letting Workday do the keyword
        search server-side keeps that to a few pages instead of fifty.
        """
        postings, seen = [], set()

        for term in (keywords or [""]):
            fetched, total = 0, None
            for page in range(self.MAX_PAGES):
                response = requests.post(
                    url,
                    headers={**HEADERS, "Content-Type": "application/json",
                             "Accept": "application/json"},
                    json={"appliedFacets": {}, "limit": self.PAGE_SIZE,
                          "offset": page * self.PAGE_SIZE, "searchText": term},
                    timeout=TIMEOUT,
                )
                response.raise_for_status()
                payload = response.json()

                # Only the first page reports the result count; later pages send total=0.
                if total is None:
                    total = payload.get("total") or 0

                batch = payload.get("jobPostings", [])
                fetched += len(batch)
                for job in batch:
                    path = job.get("externalPath")
                    if path and path not in seen:
                        seen.add(path)
                        postings.append(job)

                if len(batch) < self.PAGE_SIZE or fetched >= total:
                    break

        return postings

    def extract(self, payload):
        jobs = []
        for job in payload:
            path = job.get("externalPath")
            link = f"{self.host}/{self.site}{self.strip_query(path)}" if path else None
            jobs.append((job.get("title"), job.get("locationsText"), link))
        return jobs


PARSERS_BY_ATS = {cls.ats: cls for cls in (
    GreenhouseParser, LeverParser, AshbyParser, SmartRecruitersParser, WorkableParser,
    RecruiteeParser, PersonioParser, ComeetParser, WorkdayParser,
)}


def load_ats_parsers(companies=COMPANIES):
    """Build a parser instance for every company listed in config/companies.py."""
    parsers = []
    for company in companies:
        ats = company.get("ats")
        parser_cls = PARSERS_BY_ATS.get(ats)
        if parser_cls is None:
            logger.warning(f"⚠️ Unknown ATS '{ats}' for {company.get('name')}, skipping")
            continue

        extra = {k: v for k, v in company.items() if k not in ("name", "ats", "token")}
        parsers.append(parser_cls(company["name"], company["token"], extra))

    logger.info(f"🗂 Loaded {len(parsers)} ATS-backed companies")
    return parsers
