import bs4

from options import ObjectDict
import parser


class Parser(parser.AbstractParser):
    def parse(self, raw_data):
        html = bs4.BeautifulSoup(raw_data, "lxml")
        data = ObjectDict()

        # find price
        elem = html.select("div.unified_price_row.red_price > span.price_column.right")[0]
        data.price = parse_price(elem.text)

        # find in stock
        elem = html.select("div.deliveryMessage")[0]
        data.in_stock = "out of stock" not in elem.text.lower()

        if not data:
            return []
        return [data]


def parse_price(price):
    price = price.replace("$", "")
    return float(price)
