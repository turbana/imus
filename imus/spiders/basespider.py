# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

import scrapy


class ImusBaseSpider(scrapy.Spider, ABC):
    @abstractmethod
    def item_match(self, item):
        pass
