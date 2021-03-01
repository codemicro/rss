import datetime
import json
import os
import sys
import time

import feedparser
import css_inline

import template

__VERSION__ = "v0.0.1"

# load/create config

user_home_dir = os.path.expanduser('~')
config_file_location = os.path.join(user_home_dir, ".config", "feedAggregator.json")

print("loading", config_file_location)

configuration = {}

if os.path.exists(config_file_location):
    with open(config_file_location) as f:
        configuration = json.load(f)

feeds = configuration.get("feeds", [])


def save_config():
    with open(config_file_location, "w") as f:
        json.dump(configuration, f)


def info():
    print("Configuration file:", config_file_location)
    print("Version:", __VERSION__)
    print("Python version:", sys.version)


def add(name: str, url: str):
    x = {"name": name, "url": url}
    feeds.append(x)
    print(f"Added as feed {len(feeds)}")
    configuration["feeds"] = feeds
    save_config()


def show():
    x = []
    for i, r in enumerate(feeds, start=1):
        x.append(f"{i}: {r['name']} - {r['url']}")
    print("\n".join(x))


def remove(id: int):
    x = feeds.pop(id-1)
    print("Removed", x)
    configuration["feeds"] = feeds
    with open(config_file_location, "w") as f:
        json.dump(configuration, f)


def generate_email():

    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    yesterday = [yesterday.day, yesterday.month, yesterday.year]

    def feed_entry_filter_func(rss_entry: feedparser.util.FeedParserDict) -> bool:
        return [
            rss_entry.published_parsed.day,
            rss_entry.published_parsed.month,
            rss_entry.published_parsed.year,
        ] == yesterday

    sections = []
    warnings = []

    start_time = time.time()
    for feed in feeds:

        d = feedparser.parse(feed["url"])

        print(feed["url"], d.status)

        if not d.status == 200:
            warnings.append(f"feed \"{feed['name']}\" returned a non-200 status code - {d.status}")
            continue

        for entry in d.entries:
            entry.published_parsed = datetime.datetime(*(entry.published_parsed[0:6]))

        new = list(filter(feed_entry_filter_func, sorted(d.entries, key=lambda x: x.published_parsed, reverse=True)))

        items = []
        for x in new:
            dt = x.published_parsed.strftime("%d%b%y %H:%M")
            items.append(template.SectionItem(x.link, x.title, dt))

        section = template.Section(feed['name'], items)

        sections.append(section)

    total_time = time.time() - start_time

    bottom_text = f"Generated in {total_time} seconds"
    print(len(warnings), feeds)
    if len(warnings) != 0:
        xrz = "<br><b>Warning:</b> "
        bottom_text += xrz + (xrz.join(warnings))

    email = template.DigestEmail("Feed digest for " + datetime.datetime.now().strftime("%d%b%y"), bottom_text, sections)

    with open("output.html", "w", encoding="utf8") as f:
        f.write(css_inline.inline(str(email)))


if __name__ == '__main__':
    import fire
    fire.Fire({
        "run": generate_email,
        "add": add,
        "show": show,
        "remove": remove,
    })
