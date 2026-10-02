"""Decode a secret message from a published Google Doc.

The doc contains a table with columns x-coordinate, Character and y-coordinate.
Plotting each character at (x, y) — with x increasing to the right and y
increasing upward, so (0, 0) is the bottom-left corner — reveals a message
written in block letters.
"""

import sys
import urllib.request
from html.parser import HTMLParser


class _TableParser(HTMLParser):
    """Collects the text of every table cell, grouped into rows."""

    def __init__(self):
        super().__init__()
        self.rows = []
        self._row = None
        self._cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None:
            self._row.append("".join(self._cell).strip())
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def _fetch(url):
    with urllib.request.urlopen(url) as response:
        return response.read().decode("utf-8")


def _parse_points(html):
    """Return a list of (x, y, char) tuples from the doc's table."""
    parser = _TableParser()
    parser.feed(html)

    points = []
    columns = None
    for row in parser.rows:
        if columns is None:
            # Locate the header row and remember which column holds what,
            # so the parser doesn't depend on column order.
            headers = [cell.lower() for cell in row]
            if any("x-coordinate" in h for h in headers):
                columns = {
                    "x": next(i for i, h in enumerate(headers) if "x-coordinate" in h),
                    "y": next(i for i, h in enumerate(headers) if "y-coordinate" in h),
                    "char": next(i for i, h in enumerate(headers) if "character" in h),
                }
            continue
        try:
            x = int(row[columns["x"]])
            y = int(row[columns["y"]])
        except (IndexError, ValueError):
            continue
        char = row[columns["char"]] or " "
        points.append((x, y, char))
    return points


def print_secret_message(url):
    """Fetch the Google Doc at `url` and print the character grid it describes."""
    points = _parse_points(_fetch(url))
    if not points:
        return

    width = max(x for x, _, _ in points) + 1
    height = max(y for _, y, _ in points) + 1
    grid = [[" "] * width for _ in range(height)]
    for x, y, char in points:
        grid[y][x] = char

    # y grows upward, so print the highest row first.
    for row in reversed(grid):
        print("".join(row))


if __name__ == "__main__":
    print_secret_message(
        sys.argv[1]
        if len(sys.argv) > 1
        else "https://docs.google.com/document/d/e/2PACX-1vTMOmshQe8YvaRXi6gEPKKlsC6UpFJSMAk4mQjLm_u1gmHdVVTaeh7nBNFBRlui0sTZ-snGwZM4DBCT/pub"
    )
