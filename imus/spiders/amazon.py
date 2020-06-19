# -*- coding: utf-8 -*-
import bs4

from imus.spiders.basespider import ImusBaseSpider
from imus.items import GenericProduct


class AmazonSpider(ImusBaseSpider):
    allowed_domains = ["amazon.com"]


class AmazonListingSpider(AmazonSpider):
    def parse(self, response):
        html = bs4.BeautifulSoup(response.text, "lxml")
        item = GenericProduct()
        item["store"] = "Amazon"
        item["listing"] = response.url

        sell_new = html.find("div", id="buyNew_cbb")
        sell_used = html.find("div", id="buyNew_noncbb")

        if sell_new:
            item["condition"] = "new"
            price = sell_new.find("span", id="newBuyBoxPrice").text
            item["price"] = self.parse_price(price)
        elif sell_used:
            item["condition"] = "used"
            price = sell_used.find("span").text
            item["price"] = self.parse_price(price)
        else:
            item["condition"] = None
            item["stock"] = 0
            item["price"] = None

        product_name = html.find("span", id="productTitle")
        item["name"] = product_name.text.strip()

        return item

    @staticmethod
    def parse_price(price):
        price = price.replace("$", "")
        return float(price)


class AmazonC920SSpider(AmazonListingSpider):
    name = "c920s_amazon"
    start_urls = [
        "https://www.amazon.com/Logitech-C920S-Webcam-Privacy-Shutter/dp/B07K95WFWM",
        "https://www.amazon.com/Logitech-C920S-Webcam-Privacy-Shutter/dp/B085TFF7M1",
    ]

    def item_match(self, item):
        return item["condition"] == "new" and item["price"] < 80.00
