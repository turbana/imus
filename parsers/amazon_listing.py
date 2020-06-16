import bs4

from options import ObjectDict
import parser


class Parser(parser.AbstractParser):
    def parse(self, raw_data):
        html = bs4.BeautifulSoup(raw_data, "lxml")
        data = ObjectDict()

        # check for item sold new
        elem = html.find("div", id="buyNew_cbb")
        if elem:
            data.condition = "new"
            price = elem.find("span", id="newBuyBoxPrice").text
            data.price = parse_price(price)

        # check for item sold used
        elem = html.find("div", id="buyNew_noncbb")
        if elem:
            data.condition = "used"
            price = elem.find("span").text
            data.price = parse_price(price)

        if not data:
            return []
        return [data]


def parse_price(price):
    price = price.replace("$", "")
    return float(price)
