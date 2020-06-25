# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from collections import Iterable
from urllib.parse import urlparse
from os.path import dirname

from scrapy import Spider, Item, Request
from scrapy_selenium import SeleniumRequest


class BaseSpider(Spider, ABC):
    notification_expires = "1d"

    @property
    def _notification_expires(self):
        expires = self.notification_expires
        if not expires:
            return 0
        seconds = {
            "s": 1,
            "m": 60,
            "h": 60*60,
            "d": 60*60*24,
            "w": 60*60*24*7,
            "y": 60*60*24*365.25,
        }
        value, unit = int(expires[:-1]), expires[-1]
        return value * seconds[unit]

    def parse(self, response, *args, **kwargs):
        results = self._gather_responses(response, args, kwargs)
        return self._gather_matches(results)

    def _gather_responses(self, response, args, kwargs):
        """ call `self.parse_response` and collect the results. """
        result = self.parse_response(response, *args, **kwargs)
        if not result:
            return []
        if isinstance(result, Item):
            return (result, )
        if not isinstance(result, Iterable):
            klass_name = self.__class__.__name__
            raise ValueError(
                "Expected {0}.parse_response() to return either an Item or "
                "Iterable, received: {1}".format(
                    klass_name, type(result)
                ))
        return result

    def _gather_matches(self, results):
        """ call `self.matches` and collect the results. """
        for obj in results:
            return_values = self.matches(obj)
            if not isinstance(return_values, Iterable):
                return_values = (return_values, )
            for ret in return_values:
                if isinstance(ret, bool) and ret:
                    yield obj
                elif isinstance(ret, (Item, Request)):
                    yield ret

    @abstractmethod
    def parse_response(self, response):
        pass

    @abstractmethod
    def matches(self, item):
        pass

    @staticmethod
    def relative_url(url):
        parts = urlparse(url)
        dparts = parts._asdict()
        ret = "{scheme}://{netloc}".format(**dparts)
        if parts.port:
            ret += ":{port}".format(**dparts)
        if parts.path:
            ret += dirname(parts.path)
        return ret


class SeleniumSpider(BaseSpider):
    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(url=url, callback=self.parse)
