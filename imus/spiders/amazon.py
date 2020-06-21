# -*- coding: utf-8 -*-
from imus.spiders.basespider import ImusBaseSpider
from imus.items import GenericProduct


class AmazonSpider(ImusBaseSpider):
    allowed_domains = ["amazon.com"]


class AmazonListingSpider(AmazonSpider):
    def parse(self, response):
        item = GenericProduct()
        item["store"] = "Amazon"
        item["listing"] = response.url

        sell_new = response.css("div#buyNew_cbb")
        sell_used = response.css("div#buyNew_noncbb")

        if sell_new:
            item["condition"] = "new"
            item["in_stock"] = True
            price = sell_new.css("span#newBuyBoxPrice::text").get()
            item["price"] = self.parse_price(price)
        elif sell_used:
            item["condition"] = "used"
            item["in_stock"] = True
            price = sell_used.css("span::text").get()
            item["price"] = self.parse_price(price)
        else:
            item["condition"] = None
            item["in_stock"] = False
            item["price"] = None

        product_name = response.css("span#productTitle::text").get()
        item["name"] = product_name.strip()

        yield from self.matches(item)

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

    def matches(self, item):
        if item["in_stock"] and item["condition"] == "new" and item["price"] < 80.00:
            yield item
