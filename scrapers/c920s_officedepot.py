from parsers import officedepot_listing
import scraper


URL = "https://www.officedepot.com/a/products/4904248/Logitech-C920S-Pro-HD-150-Megapixel/"
NOTIFY_TIME = "1d"


class Scraper(scraper.AbstractScraper):
    def __init__(self):
        super().__init__(URL, parser=officedepot_listing)

    def match(self, data):
        return data.in_stock and data.price < 80.0

    def action(self, data):
        subject = "OfficeDepot is listing C920S in stock for $%1.02f" % data.price
        self.notify(title=subject, body=URL, suppress_time=NOTIFY_TIME)
