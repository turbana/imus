# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import subprocess

from fake_useragent import UserAgent
from selenium.webdriver import Firefox, FirefoxOptions, FirefoxProfile
from scrapy import signals
from scrapy.exceptions import IgnoreRequest, NotConfigured
from scrapy_selenium.middlewares import SeleniumMiddleware


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


class CustomSeleniumMiddleware(SeleniumMiddleware):
    def __init__(self, driver_name, driver_executable_path, driver_arguments,
                 browser_executable_path):
        self.driver_name = driver_name
        self.driver_executable_path = driver_executable_path
        self.driver_arguments = driver_arguments
        self.browser_executable_path = browser_executable_path
        self.initialized = False
        self.driver = None

    @classmethod
    def from_crawler(cls, crawler):
        middleware = super().from_crawler(crawler)
        crawler.signals.connect(middleware.spider_opened, signals.spider_opened)
        return middleware

    def spider_opened(self, spider):
        if self.initialized:
            return
        self.__init_driver()

    def __init_driver(self):
        if self.driver_name.lower() != "firefox":
            raise NotConfigured("SELENIUM_DRIVER_NAME must be set to 'firefox'")
        options = FirefoxOptions()
        if self.browser_executable_path:
            options.binary_location = self.browser_executable_path
        for arg in self.driver_arguments:
            options.add_argument(arg)

        useragent = UserAgent()
        profile = FirefoxProfile()
        profile.set_preference("general.useragent.override", useragent.random)

        self.driver = Firefox(executable_path=self.driver_executable_path,
                              firefox_options=options, firefox_profile=profile)
        self.initialized = True
