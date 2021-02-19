import datetime
import feedparser
import css_inline
import template

yesterday = datetime.date.today() - datetime.timedelta(days=1)
yesterday = [yesterday.day, yesterday.month, yesterday.year]


def filter_func(entry: feedparser.util.FeedParserDict) -> bool:
    entry.published_parsed = datetime.datetime(*(entry.published_parsed[0:6]))
    return [
        entry.published_parsed.day,
        entry.published_parsed.month,
        entry.published_parsed.year,
    ] == yesterday

feeds = open("feeds.txt").read().strip().split("\n")
sections = []
warnings = ""

for feed in feeds:

    d = feedparser.parse(feed)

    if not d.status == 200:
        warnings.append(f"Warning: non-200 status code - {d.status} ({feed})")
        continue

    new = list(filter(filter_func, sorted(d.entries, key=lambda x: x.published_parsed, reverse=True)))
    section = template.Section(d.feed.title, [template.SectionItem(x.link, x.title, x.published) for x in new])

    sections.append(section)

email = template.DigestEmail("This is a temporary title", "helo bottom text", [])

with open("output.html", "w", encoding="utf8") as f: 
    f.write(css_inline.inline(str(email)))
