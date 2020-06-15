from abc import ABC, abstractmethod
import requests

import notifications


class FetchError(Exception):
    pass


class AbstractScraper(ABC):
    def __init__(self, url, parser):
        self.url = url
        self.parser_module = parser
        print("url=%s, parser=%s" % (url, parser))

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
        page = requests.get(url)
        if page.status_code != 200:
            raise FetchError("received status code of %s from %s" % (
                page.status_code, url))
        open("data", "wb").write(page.content)
        return page.content

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
                self.action(data)
