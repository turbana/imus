from abc import ABC, abstractmethod
import logging
import requests

import notifications


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
        return open("data").read()
        logging.info("fetching %s" % url)
        http_headers = {"User-Agent": options.user_agent}
        page = requests.get(url, headers=http_headers)
        if page.status_code != 200:
            message = "received status code of %s from %s" % (
                page.status_code, url)
            logging.error(message)
            raise FetchError(message)
        open("data", "wb").write(page.content)
        logging.debug("received %d bytes" % len(page.content))
        return str(page.content)

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
