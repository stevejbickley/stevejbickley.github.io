"""Finish standards-mode HTML and fingerprint assets for GitHub Pages."""
import hashlib
from pathlib import Path
import re


def finalize_site(root: Path) -> None:
    output = root / "docs"
    generated = root / "assets" / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    published_assets = output / "assets" / "generated"
    published_assets.mkdir(parents=True, exist_ok=True)

    replacements = {}
    for filename in ("styles.css", "site.js"):
        source = root / "assets" / filename
        payload = source.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()[:12]
        fingerprint = f"{source.stem}.{digest}{source.suffix}"
        (generated / fingerprint).write_bytes(payload)
        replacements[filename] = f"assets/generated/{fingerprint}"

    # Retain older versions so previously cached HTML still has its assets.
    for asset in generated.iterdir():
        if asset.is_file():
            (published_assets / asset.name).write_bytes(asset.read_bytes())

    for page in output.glob("*.html"):
        content = page.read_text(encoding="utf-8")
        for filename, url in replacements.items():
            stem, extension = filename.rsplit(".", 1)
            pattern = rf'(["\'])assets/(?:generated/)?{stem}(?:\.[0-9a-f]{{12}})?\.{extension}(?:\?[^"\']*)?\1'
            content = re.sub(pattern, lambda match: f"{match[1]}{url}{match[1]}", content)
        # Quarto 1.3's HTML postprocessor drops the custom template's doctype.
        if not content.lstrip().lower().startswith("<!doctype html>"):
            content = "<!doctype html>\n" + content
        content = "\n".join(line.rstrip() for line in content.splitlines()) + "\n"
        page.write_text(content, encoding="utf-8")

    (output / ".nojekyll").touch()


if __name__ == "__main__":
    finalize_site(Path(__file__).resolve().parents[1])
