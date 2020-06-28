# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from urllib.parse import urlparse
import subprocess

from fake_useragent import UserAgent
from scrapy import signals
from scrapy.exceptions import IgnoreRequest, NotConfigured
from scrapy.http import HtmlResponse
from scrapy_selenium.http import SeleniumRequest
from scrapy_selenium.middlewares import SeleniumMiddleware
from selenium.webdriver import FirefoxOptions
from seleniumwire.webdriver import Firefox


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

        self.options = options

        self.driver = Firefox(executable_path=self.driver_executable_path,
                              firefox_options=options)
        self.initialized = True

    def process_request(self, request, spider):
        if not isinstance(request, SeleniumRequest):
            return None

        # remove old seleniumwire responses
        del self.driver.requests

        # setup seleniumwire to only save responses to the host we're hitting
        url = urlparse(request.url)
        self.driver.scopes = ['{0}://.*{1}'.format(url.scheme, url.netloc)]

        # setup fake User-Agent
        self.driver.header_overrides = {
            "User-Agent": UserAgent().random,
        }

        # call selenium for the request
        response = super().process_request(request, spider)

        # call seleniumwire for the response
        http_request = self.driver.wait_for_request(response.url)
        headers = http_request.response.headers

        # the remote webserver might send us compressed data, but selenium
        # seems to only return text, so just drop the Content-Encoding header
        if headers.get("Content-Encoding", "").lower() == "gzip":
            del headers["Content-Encoding"]

        # and finally return a response with headers suitable for caching
        return HtmlResponse(
            url=response.url,
            body=response.body,
            encoding="utf-8",
            request=request,
            headers=headers
        )
