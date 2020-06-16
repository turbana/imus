from abc import ABC, abstractmethod
import logging
import os.path
import requests
import urllib3

import fake_useragent

import notifications
from options import options
import util


AMAZON_BLOCKED_MESSAGE = "To discuss automated access to Amazon data please contact"


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
            logging.info("using cache file %s for %s" % (
                cache_filename, url))
            return open(cache_filename).read()

        # fetch page
        logging.info("fetching %s" % url)
        # http_headers = {"User-Agent": options.user_agent}
        http_headers = self.http_headers(url)
        logging.debug("http-headers: %s" % http_headers)
        page = requests.get(url, headers=http_headers,
                            timeout=options.requests_timeout)
        if page.status_code != 200:
            message = "received status code of %s from %s" % (
                page.status_code, url)
            logging.error(message)
            raise FetchError(message)

        # check for blocked response
        if AMAZON_BLOCKED_MESSAGE in page.text:
            message = "request blocked by amazon: %s" % url
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
            logging.debug("found data: %s" % data)
            if self.match(data):
                logging.info("found match")
                self.action(data)

    @staticmethod
    def http_headers(url):
        return {
            # "user-agent": options.user_agent,
            "user-agent": fake_useragent.UserAgent().random,
            "authority": urllib3.util.parse_url(url).host,
            "Referer": url,
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "dnt": "1",
            "upgrade-insecure-requests": "1",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-dest": "document",
            "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
        }
