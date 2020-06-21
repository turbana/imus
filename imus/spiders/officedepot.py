# -*- coding: utf-8 -*-
from imus.spiders.basespider import ImusBaseSpider
from imus.items import GenericProduct


class OfficeDepotSpider(ImusBaseSpider):
    allowed_domains = ["officedepot.com"]


class OfficeDepotListingSpider(OfficeDepotSpider):
    def parse(self, response):
        item = GenericProduct()
        item["store"] = "OfficeDepot"
        item["listing"] = response.url
        item["condition"] = "new"

        # find price
        price = response.css("div.unified_price_row.red_price > span.price_column.right::text").get()
        item["price"] = self.parse_price(price)

        # find in stock
        delivery = response.css("div.deliveryMessage > span::text").get()
        item["in_stock"] = "out of stock" not in delivery.lower()

        # find product name
        heading = response.css("div#skuHeading > h1::text").get()
        item["name"] = heading.strip()

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
