# -*- coding: utf-8 -*-

from datetime import datetime

from imus.spiders import SeleniumSpider
from imus.items import JobBlurb


class IndeedSpider(SeleniumSpider):
    allowed_domains = ["indeed.com"]

    def parse(self, response):
        for posting in response.css("div.jobsearch-SerpJobCard"):
            blurb = JobBlurb()
            blurb["source"] = "indeed"
            blurb["title"] = self.select(posting, "h2.title > a.jobtitle")
            blurb["company"] = self.select(posting, "div.sjcl span.company")
            blurb["location"] = self.select(posting, "div.sjcl .location")
            remote = self.select(posting, "div.sjcl span.remote")
            blurb["is_remote"] = "available" in remote.lower()
            blurb["salary_info"] = self.select(posting, "div.salarySnippet")
            blurb["company_rating"] = self.select(posting, "span.ratingsContent")
            blurb["summary"] = self.select(posting, "div.summary")
            blurb["listing"] = "https://indeed.com" + posting.css("a.jobtitle").xpath("./@href").get()
            blurb["is_ad"] = "pagead" in blurb["listing"]
            blurb["scraped_at"] = datetime.now()

            # yield blurb
            return blurb

    @staticmethod
    def select(elem, selector):
        return "".join(elem.css(selector).xpath(".//text()").getall()).strip()


class IndeedC920SSpider(IndeedSpider):
    name = "jobs_indeed"
    start_urls = [
        "https://www.indeed.com/jobs?q=software+engineer&l=Kent%2C+WA",
    ]
    title_must_contain = [
        "software", "programmer", "programming", "develop", "devop",
        "engineer", "game"
    ]
    title_must_not_contain = [
        "senior", "director", "lead", "test"
    ]

    def matches(self, item):
        title = item["title"].lower()
        good = any(s in title for s in self.title_must_contain)
        bad = any(s in title for s in self.title_must_not_contain)
        return good and not bad
        # if good and not bad:
        #     print(item)
        #     pass
