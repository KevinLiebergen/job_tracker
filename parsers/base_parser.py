class BaseParser:
    name = "base"

    def __init__(self, driver=None):
        self._driver = driver

    @property
    def driver(self):
        if self._driver is None:
            from src.driver_factory import get_driver
            self._driver = get_driver()
        return self._driver

    def build_urls(self, keywords):
        """Return a list of URLs to crawl."""
        raise NotImplementedError

    def parse(self, url, keywords, driver=None, should_quit=False):
        """Return a list of job dicts extracted from HTML."""
        raise NotImplementedError
