import logging


class DroppedItemsLoggingFilter(logging.Filter):
    """ By default Items dropped with a DropItem exception are logged as
    WARNINGs. Sometimes we want to ignore Items as a normal course, this filter
    changes them into DEBUG. """

    prefixes = (
        # found an Item we're not interested in
        "Dropped: Item did not match",
        # tried to email a duplicate Item
        "Dropped: Already sent notification",
    )

    def filter(self, record):
        f = record.getMessage().startswith
        if any(map(f, self.prefixes)):
            record.levelname = "DEBUG"
            record.levelno = logging.DEBUG
        return True


def setup():
    logging.getLogger("scrapy.core.scraper").addFilter(DroppedItemsLoggingFilter())
