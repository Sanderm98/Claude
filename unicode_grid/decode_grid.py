"""Decode a secret message drawn as a grid of Unicode characters in a Google Doc.

The published doc contains a table with the columns "x-coordinate",
"Character" and "y-coordinate". x increases to the right and y increases
upward, so (0, 0) is the bottom-left corner of the printed grid.
"""

import sys
import urllib.request
from html.parser import HTMLParser


class _TableParser(HTMLParser):
    """Collects the text of every table cell, grouped by row."""

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
            if self._row:
                self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def fetch_html(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")


def parse_cells(html):
    """Return a list of (x, y, char) tuples from the doc's table."""
    parser = _TableParser()
    parser.feed(html)
    rows = parser.rows
    if not rows:
        raise ValueError("No table found in document")

    # Locate columns by header name rather than assuming their order.
    header = [h.lower() for h in rows[0]]
    x_col = next(i for i, h in enumerate(header) if h.startswith("x"))
    y_col = next(i for i, h in enumerate(header) if h.startswith("y"))
    c_col = next(i for i, h in enumerate(header) if "char" in h)

    cells = []
    for row in rows[1:]:
        if len(row) <= max(x_col, y_col, c_col):
            continue
        try:
            x, y = int(row[x_col]), int(row[y_col])
        except ValueError:
            continue
        cells.append((x, y, row[c_col] or " "))
    return cells


def build_grid(cells):
    """Return the grid as a list of strings, top row first."""
    if not cells:
        return []
    width = max(x for x, _, _ in cells) + 1
    height = max(y for _, y, _ in cells) + 1
    grid = [[" "] * width for _ in range(height)]
    for x, y, ch in cells:
        grid[y][x] = ch
    # y = 0 is the bottom row, so print rows in reverse.
    return ["".join(row) for row in reversed(grid)]


def print_secret_message(url):
    """Fetch the Google Doc at `url` and print its character grid."""
    for line in build_grid(parse_cells(fetch_html(url))):
        print(line)


if __name__ == "__main__":
    print_secret_message(sys.argv[1])
