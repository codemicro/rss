import re
from typing import Dict, List, TextIO

parsing_regex = re.compile(r"([a-zA-Z0-9]+): *\n?((?:(?:    |\t).*\n?)*)")


def _remove_prefixes(text: str, *prefixes: List[str]) -> str:
    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix) :]
    return text


def string(input_string: str) -> Dict[str, str]:
    o = {x[0]: x[1] for x in parsing_regex.findall(input_string)}
    for key in o:
        o[key] = "\n".join(
            [_remove_prefixes(x, "    ", "\t") for x in o[key].split("\n")]
        )
    return o


def file(f: TextIO) -> Dict[str, str]:
    return string(f.read())
