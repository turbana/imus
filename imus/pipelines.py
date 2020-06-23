# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
import os.path
import time

from scrapy.exceptions import DropItem
from scrapy.mail import MailSender
from scrapy.utils.project import data_path

from imus.items import Emailable


class SendEmailPipeline(object):
    def __init__(self, settings):
        self.cache_dir = data_path(settings.get("DUPLICATECACHE_DIR"),
                                   createdir=True)
        self.send_email = settings.get("SEND_NOTIFICATIONS", False)
        self.mailer = MailSender.from_settings(settings)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_item(self, item, spider):
        if not isinstance(item, Emailable):
            raise DropItem("%s received non-Emailable item" % (
                self.__class__.__name__))
        elif self.is_in_cache(item) and not self.is_expired(item, spider.notification_expires):
            filename = os.path.basename(self.cache_filename(item))
            raise DropItem("Already sent notification for item (%s), ignoring" % (
                filename))

        if self.send_email:
            d = self.mailer.send(to=spider.settings.get("MAIL_TO"),
                                 subject=item.email_subject,
                                 body=item.email_body)
            # add item to notification cache after a successful email
            def put_in_cache_impl(result, item):
                self.put_in_cache(item)
                return result
            d.addCallback(put_in_cache_impl, item)

        return item

    def is_expired(self, item, expires):
        if not expires:
            return False
        seconds = {
            "s": 1,
            "m": 60,
            "h": 60*60,
            "d": 60*60*24,
            "w": 60*60*24*7,
            "y": 60*60*24*365.25,
        }
        value, unit = int(expires[:-1]), expires[-1]
        expires_age = value * seconds[unit]
        filename = self.cache_filename(item)
        age = time.time() - os.stat(filename).st_mtime
        return expires_age < age

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
