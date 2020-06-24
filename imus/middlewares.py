# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import subprocess

from scrapy import signals
# from scrapy.downloadermiddlewares import DownloaderMiddleware
from scrapy.exceptions import IgnoreRequest


class EnsureVPNActiveMiddleware:
    def __init__(self, is_active, router_ip_cmd, public_ip_cmd):
        self.is_active = is_active
        self.router_ip_cmd = router_ip_cmd
        self.public_ip_cmd = public_ip_cmd

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            crawler.settings.get("VPN_MIDDLEWARE_ACTIVE", False),
            crawler.settings.get("VPN_MIDDLEWARE_ROUTERIP_CMD", ""),
            crawler.settings.get("VPN_MIDDLEWARE_PUBLICIP_CMD", ""),
        )

    def process_request(self, request, spider):
        if self.is_active:
            public_ip = self._call(self.public_ip_cmd)
            router_ip = self._call(self.router_ip_cmd)
            if public_ip == router_ip:
                spider.logger.error("VPN not active")
                raise IgnoreRequest("VPN not active")
            # only check the first request
            self.is_active = False

    def _call(self, cmd):
        status, output = subprocess.getstatusoutput(cmd)
        if status != 0:
            raise Exception("Non-zero exit status from: %s" % cmd)
        return output
