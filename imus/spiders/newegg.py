# -*- coding: utf-8 -*-

from imus.spiders import SeleniumSpider
from imus.items import GenericProduct


class NeweggSpider(SeleniumSpider):
    allowed_domains = ["newegg.com"]

    def parse(self, response):
        item = GenericProduct()
        item["store"] = "Newegg"
        item["listing"] = response.url

        price_parts = response.css("ul.price-main-product > li.price-current > *::text").getall()
        item["price"] = sum(float(p) for p in price_parts)
        item["name"] = response.css("div.wrapper > h1#grpDescrip_h > span::text").get().strip()
        sold_by_parts = response.css("div.featured-seller > div.label ::text").getall()
        # should either get:
        ## ["sold by", "newegg"]
        # or
        ## ["sold by", _, _, "store", _, _, _]
        if len(sold_by_parts) == 2:
            item["sold_by"] = sold_by_parts[1]
        elif len(sold_by_parts) == 7:
            item["sold_by"] = sold_by_parts[3]
        stock_elem = response.css("span#landingpage-stock").get()
        item["in_stock"] = "in stock" in stock_elem.lower()

        yield from self.matches(item)


class NeweggC920SSpider(NeweggSpider):
    name = "c920s_newegg"
    notification_expires = "1d"
    start_urls = [
        "https://www.newegg.com/logitech-c920s/p/N82E16826197335?Item=N82E16826197335&Description=c920s&cm_re=c920s-_-26-197-335-_-Product",
        # "https://www.newegg.com/logitech-c920s/p/N82E16826197335",
    ]

    def matches(self, item):
        if item["in_stock"] and item["price"] < 80.00 and item["sold_by"] == item["store"]:
            yield item
