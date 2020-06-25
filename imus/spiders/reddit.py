# -*- coding: utf-8 -*-
import datetime
import json
import re

from imus.spiders import BaseSpider
from imus.items import RedditLink


REDDIT_URL = "https://www.reddit.com"

# NOTE: For reddit timestamps we need to check our datetime.now() (non-UTC)
# versus reddit's "created_utc". I'm not sure why :(


class RedditSpider(BaseSpider):
    allowed_domains = ["reddit.com"]

    def parse_response(self, response):
        now = datetime.datetime.now().timestamp()
        parsed_data = json.loads(response.text)
        for link in parsed_data["data"]["children"]:
            link = link["data"]
            item = RedditLink()
            item["title"] = link["title"]
            item["url"] = link["url"]
            item["posted"] = int(link["created_utc"])
            item["comments"] = int(link["num_comments"])
            item["comments_rate"] = item["comments"] / ((now - item["posted"]) / 60)
            item["comments_url"] = REDDIT_URL + link["permalink"]
            item["flair"] = link["link_flair_text"] or ""

            yield item


class RedditGameDeals(RedditSpider):
    name = "reddit_gamedeals"
    start_urls = ["https://www.reddit.com/r/GameDeals/new/.json"]
    notification_expires = "1w"
    match_regex = re.compile(r'\b(free\b|100%)', re.I)
    filter_regex = re.compile(r'(gift for reddit|drm[ -]*free|spend over.*get.*free|buy (two|2)( and)? get)', re.I)
    title_sub_regex = re.compile(r' {2,}')
    popular_comment_rate = 1.0
    popular_min_age = 30 * 60

    def matches(self, item):
        age = datetime.datetime.now().timestamp() - item["posted"]
        expired = "expired" in item["flair"].lower()
        title = self.title_sub_regex.sub(" ", item["title"])
        good_match = self.match_regex.search(title)
        bad_match = self.filter_regex.search(title)
        free = good_match and not bad_match
        popular = item["comments_rate"] >= self.popular_comment_rate and \
            age >= self.popular_min_age
        return not expired and (free or popular)
