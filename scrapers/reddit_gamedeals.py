import re

from parsers import reddit_subreddit_json
import scraper


URL = "https://www.reddit.com/r/GameDeals/new/.json"
REGEX = re.compile(r'\bFree[/: ]*(?!gift for reddit(?:[eo]rs)?)(?!weekend|week)\b', flags=re.IGNORECASE)
NOTIFY_TIME = "1w"


class Scraper(scraper.AbstractScraper):
    def __init__(self):
        super().__init__(URL, parser=reddit_subreddit_json)

    def match(self, data):
        return REGEX.search(data["title"])

    def action(self, data):
        # print("  - %s" % data["title"])
        body = '<a href="%s">reddit comments</a>' % data["comments"]
        if data["comments"] != data["url"]:
            body += '<br/><a href="%s">store page</a>' % data["url"]
        self.notify(title="Free Game - %s" % data["title"],
                    body=body,
                    suppress_time=NOTIFY_TIME)
