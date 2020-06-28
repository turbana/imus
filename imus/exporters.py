from datetime import datetime
from textwrap import dedent

from scrapy.exporters import BaseItemExporter


class JobsOrgModeExporter(BaseItemExporter):
    def __init__(self, stream, **kwargs):
        super().__init__(dont_fail=True, **kwargs)
        self.stream = stream
        if not self.encoding:
            self.encoding = "utf-8"

    def start_exporting(self):
        self.write(dedent("""\
        #+TITLE: Jobs Scrape Results
        #+STARTUP: overview
        #+FILETAGS: jobs
        #+TODO: TOAPPLY(t) | APPLIED(d)
        [{date:%Y-%m-%d %a %H:%M}]
        """.format(
            date=datetime.now(),
        )))

    def export_item(self, item):
        fields = dict(item)
        fields["summary"] = fields["summary"].replace("\n", " ")
        fields["remote"] = "(Remote) " if item["is_remote"] else ""
        fields["ad"] = " (advertisement)" if item["is_ad"] else ""
        self.write(dedent("""
        * TOAPPLY {title} at {company}
        :PROPERTIES:
        :job_title: {title}
        :company: {company}
        :location: {location}
        :salary_info: {salary_info}
        :is_remote: {is_remote}
        :company_rating: {company_rating}
        :source: {source}
        :is_ad: {is_ad}
        :listing: {listing}
        :END:
        [{scraped_at:%Y-%m-%d %a %H:%M}]
        [[{listing}][Submission]]

        ** Posting{ad}
        - Title :: {title}
        - Company :: {company}
        - Location :: {remote}{location}
        - Salary :: {salary_info}
        - Summary :: {summary}

        #+BEGIN_POSTING
        long posting
        goes here
        #+END_POSTING

        ** Log
        """.format(**fields)))

    def write(self, s):
        self.stream.write(s.encode(self.encoding))
