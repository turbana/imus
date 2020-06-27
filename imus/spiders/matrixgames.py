# -*- coding: utf-8 -*-
import re

from scrapy import Request

from imus.spiders import SeleniumSpider
from imus.items import ForumThread, ForumPost


class MatrixGamesSpider(SeleniumSpider):
    allowed_domains = ["matrixgames.com"]

    def parse(self, response, *args, **kwargs):
        if "forums/tt.asp" in response.url:
            yield from self.parse_forum_listing(response, *args, **kwargs)
        elif "forums/tm.asp" in response.url:
            yield from self.parse_forum_post(response, *args, **kwargs)

    def parse_forum_listing(self, response):
        # NOTE: Matrix's forums suck. They don't contain any identifying
        # classes or IDs. So we search for <a> tags pointing to a forum thread
        # (tm.asp), that are not pointing to paged thread ('mpage=?'). Then
        # we take the parent element two elements up
        rows = response.xpath("//a[@href and starts-with(@href, 'tm.asp') and not(contains(@href, 'mpage'))]/../../..")

        for elem in rows:
            item = ForumThread()

            item["pinned"] = "top" in elem.xpath("./td[3]/text()").get().lower()
            item["title"] = elem.xpath("./td[3]//a/text()").get().strip()
            item["url"] = self.build_url(
                response.url, elem.xpath("./td[3]//a/@href").get())
            item["description"] = elem.xpath("./td[3]//a/@title").get()
            item["replies"] = int(elem.xpath("./td[4]/text()").get())
            item["author"] = elem.xpath("./td[5]//a/text()").get().strip()
            item["views"] = int(elem.xpath("./td[6]/text()").get())

            yield item

    def parse_forum_post(self, response, thread=None):
        # NOTE: Same deal as parse_forum_listing(): we find <td> with class of
        # "msg", then work back up to the containing parent element. Then back
        # down for each relevant part
        post_number = 0
        rows = response.xpath("//td[@class='msg']/../../../../..")
        for elem in rows:
            post_number += 1
            post = ForumPost()
            post["thread"] = thread
            post["text"] = "\n".join(elem.xpath(".//td[@class='msg']//text()").getall()).strip()
            post["author"] = elem.xpath(".//a[@class='subhead']/text()").get()
            post["post_number"] = post_number
            post["posted_timestamp"] = elem.xpath(".//td[@class='cat']/table/tr/td/span/text()").get()

            yield post

    def build_url(self, full_url, relative_url):
        base_url = self.relative_url(full_url)
        if not base_url.endswith("/"):
            base_url += "/"
        return base_url + relative_url


class MatrixGamesShadowEmpireRelease(MatrixGamesSpider):
    name = "shadow_empire_release"
    start_urls = [
        "https://www.matrixgames.com/forums/tt.asp?forumid=1753",
    ]
    notification_expires = None
    version_regex = re.compile('\\bv?([0-9.]+)\\b', flags=re.IGNORECASE)

    def matches(self, item):
        if isinstance(item, ForumThread):
            title = item["title"].lower()
            version = self.version_regex.search(title)
            version = version and version.group(1)
            name = "shadow empire" in title
            release = "release" in title or "available" in title
            if item["pinned"] and name and release and version:
                return Request(item["url"], cb_kwargs=dict(thread=item))
        elif isinstance(item, ForumPost):
            return item["post_number"] == 1
