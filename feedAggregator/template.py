from typing import List
import chevron
import os

import part_parse

# load section file
parts = part_parse.file(open(os.path.join(os.path.dirname(__file__), "sections.part.html")))

NO_UPDATED_FEEDS_TEXT = "No feed updates!"


class SectionItem:
    url: str
    url_text: str
    text: str

    def __init__(self, url: str, url_text: str, text: str) -> None:
        self.url = url
        self.url_text = url_text
        self.text = text

    def vars(self):
        x = vars(self)
        # this is solely so I could have idiomatic naming schemes in both the template and python places
        x["urlText"] = x["url_text"]
        del x["url_text"]
        return x


class Section:
    title: str
    items: List[SectionItem]

    def __init__(self, title: str, items: List[SectionItem]) -> None:
        self.title = title
        self.items = items

    def __str__(self) -> str:
        table_items_string = ""
        num_items = len(self.items)
        for i, item in enumerate(self.items):

            variables = item.vars()
            if i != num_items - 1:
                variables["tableSpacer"] = parts["tableSpacer"]

            table_items_string += chevron.render(parts["tablePart"], variables) + "\n"

        if table_items_string == "":
            return ""

        return chevron.render(
            parts["section"], {"sectionTitle": self.title, "tableItems": table_items_string}
        )


class DigestEmail:
    title: str
    sections: List[Section]
    bottom_text: str

    def __init__(self, title: str, bottom_text: str, sections: List[Section]) -> None:
        self.title = title
        self.sections = sections
        self.bottom_text = bottom_text

    def __str__(self) -> str:

        sects = sorted(self.sections, key=lambda x: x.title)
        combi = list(filter(lambda x: x != "", [str(x) for x in sects]))

        return chevron.render(
            parts["email"],
            {
                "mailTitle": self.title,
                "mailContent": parts["sectionJoin"].join([""] + (combi if len(combi) != 0 else [NO_UPDATED_FEEDS_TEXT])),  # [""] adds an extra line at the top of the email
                "bottomText": self.bottom_text
            },
        )
