import datetime
import feedparser
import css_inline
import template

feeds = open("feeds.txt").read().strip().split("\n")

email = template.DigestEmail("This is a temporary title", "helo bottom text", [])

yesterday = datetime.date.today() - datetime.timedelta(days=1)
yesterday = [yesterday.day, yesterday.month, yesterday.year]


def filter_func(entry):
    entry.published_parsed = datetime.datetime(*(entry.published_parsed[0:6]))
    return [
        entry.published_parsed.day,
        entry.published_parsed.month,
        entry.published_parsed.year,
    ] == yesterday


for feed in feeds:
    print(f"Loading {feed}")

    d = feedparser.parse(feed)

    if not d.status == 200:
        print("Warning: non-200 status code -", d.status)
        continue

    d.entries = list(sorted(d.entries, key=lambda x: x.published_parsed, reverse=True))
    new = list(filter(filter_func, d.entries))

    section = template.Section(d.feed.title, [template.SectionItem(x.link, x.title, x.published) for x in d.entries])

    email.sections.append(section)

with open("output.html", "w", encoding="utf8") as f: 
    f.write(css_inline.inline(str(email)))
