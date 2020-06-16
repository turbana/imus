from abc import ABC, abstractmethod
import logging
import os.path
import requests

import notifications
from options import options
import util


class FetchError(Exception):
    pass


class AbstractScraper(ABC):
    def __init__(self, url, parser):
        self.url = url
        self.parser_module = parser
        logging.debug("configured scraper with parser=%s, url=%s" % (
            parser.__name__, url))

    @abstractmethod
    def action(self, data):
        pass

    @abstractmethod
    def match(self, data):
        pass

    def parse(self, raw_data):
        parser = self.parser_module.Parser()
        return parser.parse(raw_data)

    def fetch(self, url):
        # check cache
        cache_filename = os.path.join(options.cache_dir,
                                      util.get_hash(url) + ".html")
        if options.cache and os.path.isfile(cache_filename):
            logging.info("using cache for %s" % url)
            return open(cache_filename).read()

        # fetch page
        logging.info("fetching %s" % url)
        http_headers = {"User-Agent": options.user_agent}
        page = requests.get(url, headers=http_headers)
        if page.status_code != 200:
            message = "received status code of %s from %s" % (
                page.status_code, url)
            logging.error(message)
            raise FetchError(message)

        # save response
        logging.debug("writing %d bytes to cache file %s" % (
            len(page.content), cache_filename))
        open(cache_filename, "w").write(page.text)
        return page.text

    def notify(self, title, body, suppress_time):
        msg = {
            "title": title,
            "body": body,
            "options": {
                "suppress_time": suppress_time,
            },
        }
        notifications.notify(msg)

    def check(self):
        raw_data = self.fetch(self.url)
        data_rows = self.parse(raw_data)
        for data in data_rows:
            if self.match(data):
                logging.info("found match: %s" % data["title"])
                logging.debug(str(data))
                self.action(data)
