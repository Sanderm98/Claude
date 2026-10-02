import io
import unittest
from contextlib import redirect_stdout
from unittest import mock

import decode_grid

# Mirrors the published example doc, which draws the letter 'F'.
EXAMPLE_HTML = """
<html><body><p>Some intro text</p><table>
<tr><td><p><span>x-coordinate</span></p></td><td><p><span>Character</span></p></td>
<td><p><span>y-coordinate</span></p></td></tr>
""" + "".join(
    f"<tr><td><p><span>{x}</span></p></td><td><p><span>{c}</span></p></td>"
    f"<td><p><span>{y}</span></p></td></tr>"
    for x, c, y in [
        (0, "█", 0), (0, "█", 1), (0, "█", 2), (1, "▀", 1),
        (1, "▀", 2), (2, "▀", 1), (2, "▀", 2), (3, "▀", 2),
    ]
) + "</table></body></html>"


class DecodeGridTest(unittest.TestCase):
    def test_example_prints_F(self):
        out = io.StringIO()
        with mock.patch.object(decode_grid, "fetch_html", return_value=EXAMPLE_HTML), \
                redirect_stdout(out):
            decode_grid.print_secret_message("http://example")
        self.assertEqual(out.getvalue(), "█▀▀▀\n█▀▀ \n█   \n")


if __name__ == "__main__":
    unittest.main()
