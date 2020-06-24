import sys

from imus.spiders.reddit import RedditGameDeals


def main():
    return test_gamedeals_regex()


# run tests on free game regex's
def test_gamedeals_regex():
    should_match = (
        "[itch.io] Fumiko! ($0/100% Off)",
        "[IndieGala] Topless Hentai Mosaic (Free/100% off)",
        "[Microsoft Store] Cities: Skylines - Green Cities DLC (Free/100% Off)",
        "[IndieGala] Ubersoldier II (100% off/Free)",
        "[IndieGala] Waste Walkers Deliverance,Waste Walkers Subsistence,Adam Wolfe Complete Edition (Free)",
        "[Twitch prime] Pictoquest added on Twitch prime (free)",
    )
    should_not_match = (
        "[Fanatical] Red Hot Sale Day 3 (Including SUPERHOT VR (-50%), Stronghold Crusader HD (-80%), Star Control: Origins (-58%), Ancestors Legacy (-73%), Foxhole (-40%), Destiny 2: Beyond Light (-5%) & More. Plus spend over $10 and get Override: Mech City Brawl for free)",
        "free gift for reddit",
        "[Indiegala] Summer Girls Adult Bundle ($8.99/78% for 6 Adult DRM-FREE games, including The diary of the cheating young married woman, SIE-Hina's Online Porn Adventure, Night crawling is BAD!?, Noble Woman's Pastries, Sleeping Beauty and Night crawling is really dodgy!)",
        "[Target] Buy 2 Get 1 Free on Video Games, Books and Movies - (Excludes Nintendo first-party and most preorders)",
    )
    def matches(title):
        good_match = RedditGameDeals.match_regex.search(title)
        bad_match = RedditGameDeals.filter_regex.search(title)
        return good_match and not bad_match
    failures = 0
    for title in should_match:
        if not matches(title):
            print("error: should have matched: " + title)
            failures += 1
    for title in should_not_match:
        if matches(title):
            print("error: should not have matched " + title)
            failures += 1
    if failures:
        print("failed %d times" % failures)
    return failures


if __name__ == "__main__":
    sys.exit(main())
