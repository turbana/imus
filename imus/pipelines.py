# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os.path
import time

from scrapy.exceptions import DropItem
from scrapy.mail import MailSender
from scrapy.utils.project import data_path

from imus.items import Emailable, Cacheable


class DuplicateItemCachePipeline(object):
    def __init__(self, settings):
        self.cache_dir = data_path(settings.get("DUPLICATE_ITEM_CACHE_DIR"),
                                   createdir=True)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_item(self, item, spider):
        if not isinstance(item, Cacheable):
            return item
        filename = self.cache_filename(item, spider)
        in_cache = self.is_in_cache(filename)
        expired = in_cache and self.is_expired(filename)
        if in_cache and not expired:
            raise DropItem("Item found in cache ({}) and not expired".format(
                item.hash()))
        elif not in_cache or expired:
            spider.logger.debug("Adding item to cache: {}".format(
                item.hash()))
            expires = spider._notification_expires
            self.put_in_cache(filename, item, expires)
        return item

    def cache_filename(self, item, spider):
        hash = item.hash()
        return os.path.join(self.cache_dir, spider.name, hash[:2], hash)

    def is_expired(self, filename):
        with open(filename, "r") as f:
            expires = float(f.readline().strip())
        return expires and expires < time.time()

    def is_in_cache(self, filename):
        return os.path.exists(filename)

    def put_in_cache(self, filename, item, expires):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        # if we have a non-zero expiration: add the current time
        if expires:
            expires += time.time()
        with open(filename, "w") as f:
            f.write("{expires}\n{cls}({item})\n".format(
                expires=expires,
                cls=type(item).__name__,
                item=str(item)))


class SendEmailPipeline(object):
    def __init__(self, settings):
        self.send_email = settings.get("SEND_NOTIFICATIONS", False)
        self.mailer = MailSender.from_settings(settings)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_item(self, item, spider):
        if isinstance(item, Emailable):
            if self.send_email:
                self.mailer.send(to=spider.settings.get("MAIL_TO"),
                                 subject=item.email_subject,
                                 body=item.email_body)
            else:
                print("would have sent: %s" % (item.email_subject))
        return item
