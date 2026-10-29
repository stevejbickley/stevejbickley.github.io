"""Regression checks for stale CSS/JavaScript across GitHub Pages deployments."""
from pathlib import Path
import re
import tempfile
import unittest

from finalize import finalize_site


class FinalizeSiteTests(unittest.TestCase):
    def test_changed_assets_get_new_urls_on_every_page(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "assets").mkdir()
            (root / "docs").mkdir()
            css = root / "assets/styles.css"
            css.write_text("body { background: ivory; }\n")
            (root / "assets/site.js").write_text("document.title = 'Steve';\n")
            for name in ("index.html", "research.html"):
                (root / "docs" / name).write_text(
                    '<html><head><link href="assets/styles.css" rel="stylesheet">\n'
                    '<script src="assets/site.js" defer></script></head><body></body></html>  \n'
                )

            def urls(page):
                return re.findall(r'(?:href|src)="(assets/generated/[^\"]+)"', page.read_text())

            finalize_site(root)
            home = root / "docs/index.html"
            first_urls = urls(home)
            self.assertEqual(len(first_urls), 2)
            self.assertEqual((root / "docs" / first_urls[0]).read_bytes(), css.read_bytes())
            self.assertTrue(home.read_text().startswith("<!doctype html>\n"))
            self.assertTrue((root / "docs/.nojekyll").exists())

            css.write_text("body { background: sage; }\n")
            finalize_site(root)
            second_urls = urls(home)
            self.assertNotEqual(first_urls[0], second_urls[0])
            self.assertEqual(first_urls[1], second_urls[1])
            self.assertEqual(urls(root / "docs/research.html"), second_urls)
            self.assertTrue((root / "docs" / first_urls[0]).exists())
            self.assertEqual((root / "docs" / second_urls[0]).read_bytes(), css.read_bytes())

            previous_html = home.read_bytes()
            finalize_site(root)
            self.assertEqual(home.read_bytes(), previous_html)

            # A script-only change must also bypass previously cached JavaScript.
            (root / "assets/site.js").write_text("document.title = 'Updated';\n")
            finalize_site(root)
            third_urls = urls(home)
            self.assertEqual(second_urls[0], third_urls[0])
            self.assertNotEqual(second_urls[1], third_urls[1])
            self.assertEqual(urls(root / "docs/research.html"), third_urls)

            # Quarto can clean the output directory on a later render.
            for asset in (root / "docs/assets/generated").iterdir():
                asset.unlink()
            finalize_site(root)
            self.assertTrue(all((root / "docs" / url).exists() for url in first_urls + second_urls + third_urls))


if __name__ == "__main__":
    unittest.main()
