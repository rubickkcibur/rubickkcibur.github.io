import re
import unittest
from pathlib import Path
from urllib.parse import urlparse, unquote


REPO_ROOT = Path(__file__).resolve().parents[1]
NAVIGATION_FILE = REPO_ROOT / "_data" / "navigation.yml"
ABOUT_FILE = REPO_ROOT / "_pages" / "about.md"


def load_navigation_urls():
    entries = []
    current_title = None

    for raw_line in NAVIGATION_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        title_match = re.match(r'- title: "(.*)"', line)
        if title_match:
            current_title = title_match.group(1)
            continue

        url_match = re.match(r'url: "(.*)"', line)
        if url_match and current_title:
            entries.append((current_title, url_match.group(1)))
            current_title = None

    return entries


def load_about_anchor_ids():
    content = ABOUT_FILE.read_text(encoding="utf-8")
    return re.findall(r"""<span class=['"]anchor['"] id=['"]([^'"]+)['"]></span>""", content)


class NavigationAnchorTest(unittest.TestCase):
    def test_navigation_fragments_exist_in_about_page(self):
        about_anchor_ids = set(load_about_anchor_ids())
        missing = []

        for title, url in load_navigation_urls():
            fragment = unquote(urlparse(url).fragment)
            if not fragment:
                continue

            if fragment not in about_anchor_ids:
                missing.append((title, fragment))

        self.assertEqual([], missing, f"navigation fragments missing from about page anchors: {missing}")

    def test_about_anchor_ids_do_not_contain_whitespace(self):
        invalid_ids = [anchor_id for anchor_id in load_about_anchor_ids() if re.search(r"\s", anchor_id)]
        self.assertEqual([], invalid_ids, f"anchor ids should not contain whitespace: {invalid_ids}")


if __name__ == "__main__":
    unittest.main()
