# -*- coding: utf-8 -*-
from imus.spiders import SeleniumSpider
from imus.items import GenericProduct


class OfficeDepotSpider(SeleniumSpider):
    allowed_domains = ["officedepot.com"]

    def parse(self, response):
        item = GenericProduct()
        item["store"] = "OfficeDepot"
        item["listing"] = response.url

        # find price
        price = response.css("div.unified_price_row.red_price > span.price_column.right::text").get()
        item["price"] = self.parse_price(price)

        # find in stock
        delivery = " ".join(response.css("div.deliveryMessage").xpath(".//text()").getall()).lower()
        item["in_stock"] = "out of stock" not in delivery
        item["condition"] = "backorder" if "estimated" in delivery else "new"

        # find product name
        heading = response.css("div#skuHeading > h1::text").get()
        item["name"] = heading.strip()

        yield item

    @staticmethod
    def parse_price(price):
        price = price.replace("$", "")
        return float(price)


class OfficeDepotC920SSpider(OfficeDepotSpider):
    name = "c920s_officedepot"
    start_urls = [
        "https://www.officedepot.com/a/products/4904248/Logitech-C920S-Pro-HD-150-Megapixel/",
    ]
    notification_expires = "1d"

    def matches(self, item):
        return item["in_stock"] and item["condition"] == "new" and \
            item["price"] < 80.00
