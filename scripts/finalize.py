"""Finish the static output for standards-mode rendering and GitHub Pages."""
from pathlib import Path

output = Path(__file__).resolve().parents[1] / "docs"
for page in output.glob("*.html"):
    content = page.read_text(encoding="utf-8")
    # Quarto 1.3's HTML postprocessor drops the custom template's doctype.
    if not content.lstrip().lower().startswith("<!doctype html>"):
        content = "<!doctype html>\n" + content
    content = "\n".join(line.rstrip() for line in content.splitlines()) + "\n"
    page.write_text(content, encoding="utf-8")

(output / ".nojekyll").touch()
