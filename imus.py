import argparse
import importlib
import os
import os.path
import sys


SCRAPER_DIR = "scrapers"


def main():
    args = arguments()
    scrapers = possible_scrapers()
    scraper = args.scraper

    if args.list:
        print("Possible scrapers:")
        for scraper in sorted(scrapers):
            print("  " + scraper)
        return 0

    if scraper not in scrapers:
        print("error: scraper %s not found" % scraper)
        return 1

    print("running %s" % scraper)
    module_name = "%s.%s" % (SCRAPER_DIR, scraper)
    module = importlib.import_module(module_name)
    obj = module.Scraper()
    obj.check()


def arguments():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--scraper", help="name of scraper to run")
    group.add_argument("--list", help="list possible scrapers",
                       action="store_true")
    return parser.parse_args()


def possible_scrapers():
    base = os.path.dirname(sys.argv[0])
    scraper_dir = os.path.join(base, SCRAPER_DIR)
    return [scraper[:-3]
            for scraper in os.listdir(scraper_dir)
            if os.path.isfile(os.path.join(scraper_dir, scraper))
            and scraper.endswith(".py")
            and scraper != "__init__.py"]


if __name__ == "__main__":
    sys.exit(main())
