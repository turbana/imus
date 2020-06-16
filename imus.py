import argparse
import importlib
import logging
import logging.config
import os
import os.path
import sys
import yaml

from options import options


CONFIG_FILENAME = "options.yaml"


class ImusCloseException(Exception):
    pass


def main():
    args = arguments()
    load_options(args)
    configure_logging()
    scrapers = possible_scrapers()
    scraper = options.scraper

    if options.list_scrapers:
        print("Possible scrapers:")
        for scraper in sorted(scrapers):
            print("  " + scraper)
        return 0

    if scraper not in scrapers:
        logging.error("scraper %s not found" % scraper)
        return 1

    logging.info("starting run of %s" % scraper)
    module_name = "%s.%s" % (options.scraper_dir, scraper)
    module = importlib.import_module(module_name)
    obj = module.Scraper()
    obj.check()


def load_options(args):
    try:
        with open(CONFIG_FILENAME, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        logging.error("could not find %s" % CONFIG_FILENAME)
        raise ImusCloseException()
    options.update(config)
    options.update(vars(args))


def configure_logging():
    with open("logging.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    if options.verbosity == 1:
        config["handlers"]["console"]["level"] = "INFO"
    elif options.verbosity >= 2:
        config["handlers"]["console"]["level"] = "DEBUG"
    logging.config.dictConfig(config)


def arguments():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--scraper", help="name of scraper to run")
    group.add_argument("--list", help="list possible scrapers",
                       action="store_true", dest="list_scrapers")
    parser.add_argument("-v", "--verbosity", action="count", default=0,
                        help="increase output verbosity")
    return parser.parse_args()


def possible_scrapers():
    # XXX
    base = os.path.dirname(sys.argv[0])
    scraper_dir = os.path.join(base, options.scraper_dir)
    return [scraper[:-3]
            for scraper in os.listdir(scraper_dir)
            if os.path.isfile(os.path.join(scraper_dir, scraper))
            and scraper.endswith(".py")
            and scraper != "__init__.py"]


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ImusCloseException:
        sys.exit(1)
