# RSS Feed Aggregator

*Generate email digests for a select set of RSS feeds*

![GitHub](https://img.shields.io/github/license/codemicro/rss) ![OSS Lifecycle (branch)](https://img.shields.io/osslifecycle/codemicro/rss/master) ![Lines of code](https://img.shields.io/tokei/lines/github/codemicro/rss) 

----

This is a small collection of Python scripts that generate RSS email digests from a predefined set of feeds. When run, they will collect all RSS entries that were published the previous day, compiles them into an email and sends that to a given address.

### Installation

Prerequisites:

* Python >= 3.6
* [Poetry](https://python-poetry.org/) - `pip install poetry`

```bash
git clone https://www.github.com/codemicro/rss.git feedAggregator
poetry install
poetry run python ./feedAggregator setup # follow prompts
poetry run python ./feedAggregator add [feed name] [feed URL] # add your first feed!
poetry run python ./feedAggregator run [recipient email address] # send the first digest
```

This script is best suited to being run with `cron`.

### Hacking

Everything is contained within the `feedAggregator` module.

#### `__main__.py`

Script entry point, contains [Fire](https://github.com/google/python-fire) CLI and the core code to generate and send digest emails.

#### `part_parse.py`

Provides parsing functions for `sections.part.html`, a so-called part file. All the parsing is done with a single gnarly regular expression.

#### `sections.part.html`

A file containing multiple small templates for generating emails. The format is loosely based on the structure of a `Makefile`.

#### `template.py`

Contains classes for representing and forming emails. These can then be casted to strings to give rendered HTML based on that class' type. 

* `Section` represents a single feed in a digest email
* `SectionItem` represents a single article or item from an RSS feed, to be displayed in an email.
* `DigestEmail` represents an entire digest email.

### Licensing

This project is licensed under the MIT license. Read it in full [here](https://github.com/codemicro/rss/blob/master/LICENSE).

The contents of the file `sections.part.html` is derived from [this Postmark email template](https://github.com/wildbit/postmark-templates/blob/master/templates/plain/example/content.html), which is also covered by the MIT license.
