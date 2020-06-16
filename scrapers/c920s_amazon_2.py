import logging

from parsers import amazon_listing
import scraper


URL = "https://www.amazon.com/Logitech-C920S-Webcam-Privacy-Shutter/dp/B085TFF7M1"
NOTIFY_TIME = "1d"


class Scraper(scraper.AbstractScraper):
    def __init__(self):
        super().__init__(URL, parser=amazon_listing)

    def match(self, data):
        logging.debug("starting amazon_listing.match(%s)" % data)
        return data.condition == "new" and data.price < 80.0

    def action(self, data):
        subject = "Amazon is listing C920S in stock for $%1.02f" % data.price
        self.notify(title=subject, body=URL, suppress_time=NOTIFY_TIME)
