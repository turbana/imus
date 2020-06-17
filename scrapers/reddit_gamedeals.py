import re

from parsers import reddit_subreddit_json
import scraper


URL = "https://www.reddit.com/r/GameDeals/new/.json"
REGEX = re.compile(r'\b(?:Free|100%)[/: ]*(?!gift for reddit(?:[eo]rs)?)(?!weekend|week)\b', flags=re.IGNORECASE)
COMMENT_RATE = 1.0
MIN_AGE = 30 * 60
NOTIFY_TIME = "1w"


class Scraper(scraper.AbstractScraper):
    def __init__(self):
        super().__init__(URL, parser=reddit_subreddit_json)

    def match(self, data):
        expired = "expired" in data.flair.lower()
        free = REGEX.search(data.title)
        popular = data.comments_rate >= COMMENT_RATE and data.age >= MIN_AGE
        return not expired and (free or popular)

    def action(self, data):
        body = "%d reddit comments [%1.02fcpm] - %s" % (
            data.comments, data.comments_rate, data.comments_url)
        if data.url != data.comments_url:
            body += "\nstore page - %s" % data.url
        self.notify(data.title, body=body, suppress_time=NOTIFY_TIME)
