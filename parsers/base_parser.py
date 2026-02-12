from src.driver_factory import get_driver

class BaseParser:
    name = "base"
    driver = get_driver()

    def build_urls(self, keywords):
        """Return a list of URLs to crawl."""
        raise NotImplementedError

    def parse(self, url, keywords, driver=None):
        """Return a list of job dicts extracted from HTML."""
        raise NotImplementedError
