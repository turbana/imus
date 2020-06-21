# -*- coding: utf-8 -*-
import re

from imus.spiders.basespider import ImusBaseSpider
from imus.items import ForumThread


class MatrixGamesSpider(ImusBaseSpider):
    allowed_domains = ["matrixgames.com"]


class MatrixGamesForumSpider(MatrixGamesSpider):
    def parse(self, response):
        # NOTE: Matrix's forums suck. They don't contain any identifying
        # classes or IDs. So we search for <a> tags pointing to a forum thread
        # (tm.asp), that are not pointing to paged thread ('mpage=?'). Then
        # we take the parent element two elements up
        rows = response.xpath("//a[@href and starts-with(@href, 'tm.asp') and not(contains(@href, 'mpage'))]/../..")

        for elem in rows:
            item = ForumThread()

            item["pinned"] = "top" in elem.xpath("./td[3]/text()").get().lower()
            item["title"] = elem.xpath("./td[3]/a/text()").get().strip()
            item["url"] = self.build_url(
                response.url, elem.xpath("./td[3]/a/@href").get())
            item["description"] = elem.xpath("./td[3]/a/@title").get()
            item["replies"] = int(elem.xpath("./td[4]/text()").get())
            item["author"] = elem.xpath("./td[5]/a/text()").get().strip()
            item["views"] = int(elem.xpath("./td[6]/text()").get())

            yield item

    def build_url(self, full_url, relative_url):
        base_url = self.relative_url(full_url)
        if not base_url.endswith("/"):
            base_url += "/"
        return base_url + relative_url


class MatrixGamesShadowEmpireRelease(MatrixGamesForumSpider):
    name = "shadow_empire_release"
    start_urls = [
        "https://www.matrixgames.com/forums/tt.asp?forumid=1753",
    ]
    version_regex = re.compile('\\bv?([0-9.]+)\\b', flags=re.IGNORECASE)

    def item_match(self, item):
        title = item["title"].lower()
        version = self.version_regex.search(title)
        version = version and version.group(1)
        name = "shadow empire" in title
        release = "release" in title or "available" in title
        return item["pinned"] and name and release and version
