# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from urllib.parse import urlparse
from os.path import dirname

import scrapy


class ImusBaseSpider(scrapy.Spider, ABC):
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
