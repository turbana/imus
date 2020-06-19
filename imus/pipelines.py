# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
import logging
import os.path

from scrapy.exceptions import DropItem
from scrapy.exporters import BaseItemExporter
from scrapy.mail import MailSender
from scrapy.utils.project import data_path, get_project_settings

from imus.items import Emailable


class DroppedItemsLoggingFilter(logging.Filter):
    """ By default Items dropped with a DropItem exception are logged as
    WARNINGs. This changes them into DEBUGs. """

    prefixes = (
        "Dropped: Item did not match",
        "Dropped: Already sent notification",
    )

    def filter(self, record):
        f = record.getMessage().startswith
        if any(map(f, self.prefixes)):
            record.levelname = "DEBUG"
            record.levelno = logging.DEBUG
        return True


class VerifyMatchPipeline(object):
    """Ensure each Item match's the crawler's .match() function"""

    def __init__(self):
        logger = logging.getLogger("scrapy.core.scraper")
        logger.addFilter(DroppedItemsLoggingFilter())

    def process_item(self, item, spider):
        if spider.item_match(item):
            return item
        raise DropItem("Item did not match %s.item_match()" % (
            spider.__class__.__name__))


class SendEmailPipeline(object):
    def __init__(self, settings):
        self.cache_dir = data_path(settings.get("DUPLICATECACHE_DIR"),
                                   createdir=True)
        self.mailer = MailSender.from_settings(settings)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_item(self, item, spider):
        if not isinstance(item, Emailable):
            raise DropItem("%s received non-Emailable item" % (
                self.__class__.__name__))
        if self.is_in_cache(item):
            raise DropItem("Already sent notification for item, ignoring")
        d = self.mailer.send(to=spider.settings.get("MAIL_TO"),
                             subject=item.email_subject,
                             body=item.email_body)
        # add item to notification cache after a successful email
        def put_in_cache_impl(result, item):
            self.put_in_cache(item)
            return result
        d.addCallback(put_in_cache_impl, item)
        return item

    def is_in_cache(self, item):
        if not isinstance(item, Emailable):
            return False
        return os.path.exists(self.cache_filename(item))

    def cache_filename(self, item):
        md5 = hashlib.md5(item.email_subject.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, md5)

    def put_in_cache(self, item):
        self.touch(self.cache_filename(item))

    # taken from: http://stackoverflow.com/questions/1158076/ddg#1160227
    def touch(self, fname, mode=0o666, dir_fd=None, **kwargs):
        flags = os.O_CREAT | os.O_APPEND
        with os.fdopen(os.open(fname, flags=flags, mode=mode, dir_fd=dir_fd)) as f:
            os.utime(f.fileno() if os.utime in os.supports_fd else fname,
                     dir_fd=None if os.supports_fd else dir_fd, **kwargs)


"""
Ugh.

When we send email notifications it's near the end of the crawler's life-cycle
after all scraping and processing has occurred. Because scrapy uses twisted the
mail handler creates a Defered to send the mail. Somehow the twisted reactor
(main loop) closes down before all the mail Defered's have processed, causing
in progress IO calls on a closed socket triggering an error. See this github
scrapy issue for more information, specifically Ksianka's comments:
https://github.com/scrapy/scrapy/issues/3478.

It appears to be related to the freeing of an underlying TLS socket within
twisted's TLSMemoryBIOProtocol object. See the following pull-request:
https://github.com/twisted/twisted/pull/955.

I don't want to manually touch twisted's source (not that this is much better),
so hot-patch twisted's code with a modified version of the offending function.
The only change is to comment out the freeing of the `_tls_connection` object.
"""

from twisted.protocols.policies import ProtocolWrapper
from twisted.protocols.tls import TLSMemoryBIOProtocol

def fixed_connectionLost(self, reason):
    """
    Handle the possible repetition of calls to this method (due to either
    the underlying transport going away or due to an error at the TLS
    layer) and make sure the base implementation only gets invoked once.
    """
    if not self._lostTLSConnection:
        # Tell the TLS connection that it's not going to get any more data
        # and give it a chance to finish reading.
        self._tlsConnection.bio_shutdown()
        self._flushReceiveBIO()
        self._lostTLSConnection = True
    reason = self._reason or reason
    self._reason = None
    self.connected = False
    ProtocolWrapper.connectionLost(self, reason)

    # Breaking reference cycle between self._tlsConnection and self.
    #self._tlsConnection = None

TLSMemoryBIOProtocol.connectionLost = fixed_connectionLost
