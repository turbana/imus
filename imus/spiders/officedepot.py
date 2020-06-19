# -*- coding: utf-8 -*-
import bs4

from imus.spiders.basespider import ImusBaseSpider
from imus.items import GenericProduct


class OfficeDepotSpider(ImusBaseSpider):
    allowed_domains = ["officedepot.com"]


class OfficeDepotListingSpider(OfficeDepotSpider):
    def parse(self, response):
        html = bs4.BeautifulSoup(response.text, "lxml")
        item = GenericProduct()
        item["store"] = "OfficeDepot"
        item["listing"] = response.url

        # find price
        elem = html.select("div.unified_price_row.red_price > span.price_column.right")[0]
        item["price"] = self.parse_price(elem.text)

        # find in stock
        elem = html.select("div.deliveryMessage")[0]
        item["in_stock"] = "out of stock" not in elem.text.lower()

        # find product name
        elem = html.select("div#skuHeading > h1")[0]
        item["name"] = elem.contents[0].strip()

        return item

    @staticmethod
    def parse_price(price):
        price = price.replace("$", "")
        return float(price)


class OfficeDepotC920SSpider(OfficeDepotListingSpider):
    name = "c920s_officedepot"
    start_urls = [
        "https://www.officedepot.com/a/products/4904248/Logitech-C920S-Pro-HD-150-Megapixel/",
    ]

    def item_match(self, item):
        return item["in_stock"] and item["condition"] == "new" and item["price"] < 80.00
