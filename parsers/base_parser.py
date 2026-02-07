class BaseParser:
    name = "base"

    def build_urls(self, keywords):
        """Return a list of URLs to crawl."""
        raise NotImplementedError

    def parse(self, url, keywords, driver=None):
        """Return a list of job dicts extracted from HTML."""
        raise NotImplementedError
