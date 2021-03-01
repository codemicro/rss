import datetime
import json
import os
import sys
import time

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import css_inline
import feedparser
import html2text

import template

__VERSION__ = "0.0.1"

# load/create config

user_home_dir = os.path.expanduser("~")
config_file_location = os.path.join(user_home_dir, ".config", "feedAggregator.json")

configuration = {}

if os.path.exists(config_file_location):
    with open(config_file_location) as f:
        configuration = json.load(f)

feeds = configuration.get("feeds", [])


def save_config():
    with open(config_file_location, "w") as f:
        json.dump(configuration, f, indent=4, sort_keys=True)


def set_info():
    """
    Configures email information
    """
    configuration["email"] = {
        "host": input("Host: ").strip(),
        "port": int(input("Port: ").strip()),
        "username": input("Username: ").strip(),
        "password": input("Password: ").strip(),
        "sender": input("Sender: ").strip(),
    }
    save_config()


def info():
    """
    Shows information about the environment and software
    """
    print("Configuration file:", config_file_location)
    print("Version:", __VERSION__)
    print("Python version:", sys.version)


def add(name: str, url: str):
    """
    Adds a new RSS feed
    :param name: name of the new feed
    :param url: URL of the RSS feed
    """
    x = {"name": name, "url": url}
    feeds.append(x)
    print(f"Added as feed {len(feeds)}")
    configuration["feeds"] = feeds
    save_config()


def show():
    """
    Shows registered feeds
    """
    x = []
    for i, r in enumerate(feeds, start=1):
        x.append(f"{i}: {r['name']} - {r['url']}")
    print("\n".join(x))


def remove(id: int):
    """
    Removes a feed
    :param id: feed ID to remove
    """
    x = feeds.pop(id - 1)
    print("Removed", x)
    configuration["feeds"] = feeds
    save_config()


def generate_email(email_address: str):
    """
    Generates and sends an email digest for the previous days
    """

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

        if not d.status == 200:
            warnings.append(
                f"feed \"{feed['name']}\" returned a non-200 status code - {d.status}"
            )
            continue

        for entry in d.entries:
            entry.published_parsed = datetime.datetime(*(entry.published_parsed[0:6]))

        new = list(
            filter(
                feed_entry_filter_func,
                sorted(d.entries, key=lambda x: x.published_parsed, reverse=True),
            )
        )

        items = []
        for x in new:
            dt = x.published_parsed.strftime("%d%b%y %H:%M")
            items.append(template.SectionItem(x.link, x.title, dt))

        section = template.Section(feed["name"], items)

        sections.append(section)

    total_time = time.time() - start_time

    bottom_text = f"Generated in {total_time} seconds"
    if len(warnings) != 0:
        xrz = "<br><b>Warning:</b> "
        bottom_text += xrz + (xrz.join(warnings))

    title = "Feed digest for " + datetime.datetime.now().strftime("%d%b%y")

    email = template.DigestEmail(title, bottom_text, sections)

    email_html = css_inline.inline(str(email))
    email_text = html2text.HTML2Text().handle(email_html)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = title
    msg["From"] = configuration["email"]["sender"]
    msg["To"] = email_address

    msg.attach(MIMEText(email_text, "plain"))
    msg.attach(MIMEText(email_html, "html"))

    mail = smtplib.SMTP(configuration["email"]["host"], configuration["email"]["port"])
    mail.ehlo()
    mail.starttls()
    mail.login(configuration["email"]["username"], configuration["email"]["password"])
    mail.sendmail(msg["From"], msg["From"], msg.as_string())
    mail.quit()


if __name__ == "__main__":
    import fire

    fire.Fire(
        {
            "run": generate_email,
            "add": add,
            "show": show,
            "remove": remove,
            "info": info,
            "setup": set_info,
        }
    )
