# -*- coding: utf-8 -*-

from imus.spiders import SeleniumSpider
from imus.items import GenericProduct


class BestbuySpider(SeleniumSpider):
    allowed_domains = ["bestbuy.com"]

    def parse(self, response):
        if "You don't have permission" in response.text:
            self.logger.warning("Bestbuy blocked the request")
            return
        item = GenericProduct()
        item["store"] = "Bestbuy"
        item["listing"] = response.url

        price = response.css("div.col-xs-5.col-lg-4 div.priceView-customer-price > span::text").get()
        item["price"] = self.parse_price(price)
        item["name"] = response.css("div.sku-title > h1::text").get()
        add_cart_button = response.css("div.fulfillment-add-to-cart-button button::text").get()
        item["in_stock"] = "add to cart" in add_cart_button.lower()

        yield item

    @staticmethod
    def parse_price(price):
        price = price.replace("$", "")
        return float(price)


class BestbuyC920SSpider(BestbuySpider):
    name = "c920s_bestbuy"
    notification_expires = "1d"
    start_urls = [
        "https://www.bestbuy.com/site/logitech-c920s-hd-webcam/6321794.p?skuId=6321794",
    ]

    def matches(self, item):
        return item["in_stock"] and item["price"] < 80.00
