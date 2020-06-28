# -*- coding: utf-8 -*-

from datetime import datetime
from scrapy_selenium.http import SeleniumRequest as Request

from imus.spiders import SeleniumSpider
from imus.items import JobBlurb, JobListing


class IndeedSpider(SeleniumSpider):
    allowed_domains = ["indeed.com"]

    def parse(self, response):
        if response.url.endswith("-jobs.html"):
            yield from self.parse_search_results(response)
        elif "/viewjob" in response.url:
            yield from self.parse_job_listing(response)
        else:
            raise ValueError("{}.parse() received unknown url: {}".format(
                self.__class__.__name__, response.url))

    def parse_search_results(self, response):
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

            yield blurb

    def parse_job_listing(self, response):
        job = JobListing(response.meta["blurb"])
        parts = response.css("div#jobDescriptionText").xpath(".//text()").getall()
        job["full_listing"] = "\n".join(parts).strip()
        return [job]

    @staticmethod
    def select(elem, selector):
        return "".join(elem.css(selector).xpath(".//text()").getall()).strip()


class IndeedJobSearchSpider(IndeedSpider):
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
        if isinstance(item, JobBlurb):
            title = item["title"].lower()
            good = any(s in title for s in self.title_must_contain)
            bad = any(s in title for s in self.title_must_not_contain)
            if good and not bad:
                return Request(url=item["listing"], meta={"blurb": item})
        elif isinstance(item, JobListing):
            return True
