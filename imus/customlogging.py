import logging
import re

from scrapy.mail import MailSender
from scrapy.utils.project import get_project_settings


class DroppedItemsLoggingFilter(logging.Filter):
    """ By default Items dropped with a DropItem exception are logged as
    WARNINGs. Sometimes we want to ignore Items as a normal course, this filter
    changes them into DEBUG. """

    prefixes = (
        # tried to email a duplicate Item
        "Dropped: Already sent notification",
    )

    def filter(self, record):
        f = record.getMessage().startswith
        if any(map(f, self.prefixes)):
            record.levelname = "DEBUG"
            record.levelno = logging.DEBUG
        return True


class BufferingEmailHandler(logging.handlers.BufferingHandler):
    """ Buffer all received log records. When an item of ``flushLevel`` or
    higher is encountered: send an email with all buffered records. """

    def __init__(self, subject, flushLevel=logging.ERROR):
        super(BufferingEmailHandler, self).__init__(capacity=0)
        self.flushLevel = logging.getLevelName(flushLevel)
        self.tripped = False
        self.subject = subject

    def shouldFlush(self, record):
        # only flush on close()
        return self.tripped

    def handle(self, record):
        if record.levelno >= self.flushLevel:
            self.tripped = True
        super(BufferingEmailHandler, self).handle(record)

    def flush(self):
        self.acquire()
        try:
            if not self.buffer:
                return
            if not self.tripped:
                self.buffer = []
                return
            settings = get_project_settings()
            mailer = MailSender.from_settings(settings)
            body = "\n".join(self.format(record) for record in self.buffer)
            mailer.send(
                to=settings.get("MAIL_TO"),
                subject=self.subject,
                body=body
            )
            self.tripped = False
            self.buffer = []
        finally:
            self.release()
