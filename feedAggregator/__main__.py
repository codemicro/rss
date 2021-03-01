import datetime
import time

import feedparser
import css_inline

import template

yesterday = datetime.date.today() - datetime.timedelta(days=1)
yesterday = [yesterday.day, yesterday.month, yesterday.year]


# TODO: Config file


def filter_func(entry: feedparser.util.FeedParserDict) -> bool:
    return [
        entry.published_parsed.day,
        entry.published_parsed.month,
        entry.published_parsed.year,
    ] == yesterday


feeds = open("feeds.txt").read().strip().split("\n")
sections = []
warnings = []

stime = time.time()
for feed in feeds:

    d = feedparser.parse(feed)

    if not d.status == 200:
        warnings.append(f"Warning: non-200 status code - {d.status} ({feed})")
        continue

    for entry in d.entries:
        entry.published_parsed = datetime.datetime(*(entry.published_parsed[0:6]))

    new = list(filter(filter_func, sorted(d.entries, key=lambda x: x.published_parsed, reverse=True)))

    items = []
    for x in new:
        dt = x.published_parsed.strftime("%d%b%y %H:%M")
        items.append(template.SectionItem(x.link, x.title, dt))

    section = template.Section(d.feed.title, items)

    sections.append(section)

total_time = time.time() - stime

bottom_text = f"Generated in {total_time} seconds"
if len(warnings) != 0:
    bottom_text += "Warnings:\n" + ("\n".join(warnings))

email = template.DigestEmail("Feed digest for " + datetime.datetime.now().strftime("%d%b%y"), bottom_text, sections)

with open("output.html", "w", encoding="utf8") as f:
    f.write(css_inline.inline(str(email)))
