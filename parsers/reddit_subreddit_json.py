import json
import datetime

import parser
from options import ObjectDict


REDDIT_URL = "https://www.reddit.com"


class Parser(parser.AbstractParser):
    def parse(self, raw_data):
        now = datetime.datetime.utcnow().timestamp()
        parsed_data = json.loads(raw_data)
        for item in parsed_data["data"]["children"]:
            item = ObjectDict(item["data"])
            data = ObjectDict()
            data.title = item.title
            data.url = item.url
            data.comments_url = REDDIT_URL + item.permalink
            data.comments = item.num_comments
            data.age = now - item.created
            data.comments_rate = item.num_comments / (data.age / 60)
            data.flair = item.link_flair_text or ""
            yield data
