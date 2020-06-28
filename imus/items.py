# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from abc import ABC, abstractmethod
from hashlib import md5
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


class Cacheable(ABC):
    @property
    @abstractmethod
    def cache_on(self):
        pass

    @property
    def _cache_text(self):
        inner = "\n  ".join("{0}: {1},".format(attr, repr(self[attr]))
                            for attr in self.cache_on)
        return "{\n  " + inner + "\n}"

    def hash(self):
        return md5(self._cache_text.encode("utf-8")).hexdigest()


class RedditLink(Cacheable, Emailable, Item):
    cache_on = ("title", "url", "posted")
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


class GenericProduct(Cacheable, Emailable, Item):
    cache_on = ("store", "name", "price")
    store = Field()
    name = Field()
    price = Field()
    in_stock = Field()
    condition = Field()
    listing = Field()
    sold_by = Field()

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


class ForumThread(Cacheable, Emailable, Item):
    cache_on = ("title", "author")
    title = Field()
    author = Field()
    url = Field()
    posted = Field()
    pinned = Field()
    replies = Field()
    views = Field()
    description = Field()

    @property
    def email_subject(self):
        return "{title}".format(**self)

    @property
    def email_body(self):
        return textwrap.dedent(
            """
            {title}
            by {author}

            {url}
            """
        ).format(**self)


class ForumPost(Cacheable, Emailable, Item):
    cache_on = ("author", "posted_timestamp")
    thread = Field()
    author = Field()
    posted_timestamp = Field()
    post_number = Field()
    text = Field()

    @property
    def email_subject(self):
        return "{thread[title]}".format(**self)

    @property
    def email_body(self):
        return textwrap.dedent(
            """
            {thread[title]}
            by {author} at {posted_timestamp}
            {thread[url]}

            {text}
            """
        ).format(**self)


class JobBlurb(Cacheable, Item):
    cache_on = ("listing",)
    title = Field()
    company = Field()
    location = Field()
    summary = Field()
    salary_info = Field()
    is_remote = Field()
    company_rating = Field()
    source = Field()
    listing = Field()
    is_ad = Field()
    scraped_at = Field()


class JobListing(JobBlurb):
    full_listing = Field()
