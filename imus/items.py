# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from abc import ABC, abstractmethod
import textwrap

from scrapy import Item, Field


class Emailable(ABC):
    @property
    @abstractmethod
    def email_subject(self):
        pass

    @property
    @abstractmethod
    def email_body(self):
        pass


class RedditLink(Emailable, Item):
    title = Field()
    url = Field()
    comments = Field()
    comments_url = Field()
    comments_rate = Field()
    posted = Field()
    flair = Field()

    @property
    def email_subject(self):
        return self["title"]

    @property
    def email_body(self):
        body = "[%1.02f] %d reddit comments - %s" % (
            self["comments_rate"], self["comments"], self["comments_url"])
        if self["url"] != self["comments_url"]:
            body += "\nstore page - %s" % self["url"]
        return body


class GenericProduct(Emailable, Item):
    store = Field()
    name = Field()
    price = Field()
    in_stock = Field()
    condition = Field()
    listing = Field()

    @property
    def email_subject(self):
        return "[{store}] ${price} - {name}".format(**self)

    @property
    def email_body(self):
        return textwrap.dedent(
            """
            {store} is selling "{name}" {condition} for ${price}

            {listing}
            """
        ).format(**self)
