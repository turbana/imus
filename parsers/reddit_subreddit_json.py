import json

import parser


REDDIT_URL = "https://www.reddit.com"


class Parser(parser.AbstractParser):
    def parse(self, raw_data):
        data = json.loads(raw_data)
        for item in data["data"]["children"]:
            item = item["data"]
            yield {
                "title": item["title"],
                "url": item["url"],
                "comments": REDDIT_URL + item["permalink"],
            }
