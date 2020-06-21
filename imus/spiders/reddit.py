# -*- coding: utf-8 -*-
import datetime
import json
import re

from imus.spiders.basespider import ImusBaseSpider
from imus.items import RedditLink


REDDIT_URL = "https://www.reddit.com"


class RedditSpider(ImusBaseSpider):
    allowed_domains = ["reddit.com"]


class RedditSubredditJsonSpider(RedditSpider):
    def parse(self, response):
        now = datetime.datetime.utcnow().timestamp()
        parsed_data = json.loads(response.text)
        for link in parsed_data["data"]["children"]:
            link = link["data"]
            item = RedditLink()
            item["title"] = link["title"]
            item["url"] = link["url"]
            item["posted"] = int(link["created"])
            item["comments"] = int(link["num_comments"])
            item["comments_rate"] = item["comments"] / ((now - item["posted"]) / 60)
            item["comments_url"] = REDDIT_URL + link["permalink"]
            item["flair"] = link["link_flair_text"] or ""

            yield from self.matches(item)


class RedditGameDeals(RedditSubredditJsonSpider):
    name = "reddit_gamedeals"
    start_urls = ["https://www.reddit.com/r/GameDeals/new/.json"]
    free_game_regex = re.compile(r'\b(?:Free|100%)[/: ]*(?!gift for reddit(?:[eo]rs)?)(?!weekend|week)\b', flags=re.IGNORECASE)
    notify_comment_rate = 1.0
    notify_min_age = 30 * 60

    def matches(self, item):
        age = datetime.datetime.now().timestamp() - item["posted"]
        expired = "expired" in item["flair"].lower()
        free = self.free_game_regex.search(item["title"])
        popular = item["comments_rate"] >= self.notify_comment_rate and \
            age >= self.notify_min_age
        if not expired and (free or popular):
            yield item
