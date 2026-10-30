"""Apply consistent link indicators and external-tab behaviour to built HTML."""
from html import escape
from html.parser import HTMLParser
import re
from urllib.parse import urljoin, urlsplit


SITE_URL = "https://stevejbickley.github.io/"
NEW_TAB_NOTE = '<span class="visually-hidden"> (opens in a new tab)</span>'
VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


class _Anchors(HTMLParser):
    """Record anchor ranges without reserializing scripts or the rest of a page."""

    def __init__(self, content):
        super().__init__(convert_charrefs=False)
        self.offsets = [0]
        for line in content.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.stack = []
        self.anchors = []

    def source_offset(self):
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()
        navigation = tag == "nav" or "page-jumps" in classes
        if self.stack:
            navigation = navigation or self.stack[-1][1]
        anchor = None
        if tag == "a":
            start = self.source_offset()
            anchor = {
                "start": start,
                "body_start": start + len(self.get_starttag_text()),
                "attrs": attributes,
                "navigation": navigation or bool({"brand", "skip-link"} & set(classes)),
            }
        if tag not in VOID_ELEMENTS:
            self.stack.append((tag, navigation, anchor))

    def handle_startendtag(self, tag, attrs):
        # Self-closing elements contain no anchor text or navigation descendants.
        pass

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] != tag:
                continue
            anchor = self.stack[index][2]
            if anchor is not None:
                anchor["body_end"] = self.source_offset()
                self.anchors.append(anchor)
            del self.stack[index:]
            break


def normalize_site_links(content, site_url=SITE_URL):
    parser = _Anchors(content)
    parser.feed(content)
    home = urlsplit(site_url)
    replacements = []
    for anchor in parser.anchors:
        attrs = anchor["attrs"].copy()
        href = attrs.get("href")
        if not href:
            continue  # The image dialog sets its full-resolution URL at runtime.
        destination = urlsplit(urljoin(site_url, href))
        if destination.scheme not in {"http", "https"}:
            continue  # Email and other native protocols keep their normal behaviour.
        external = destination.hostname != home.hostname
        body = content[anchor["body_start"]:anchor["body_end"]]
        original_body = body
        if external:
            attrs["target"] = "_blank"
            rel = attrs.get("rel", "").split()
            if "noopener" not in rel:
                rel.append("noopener")
            attrs["rel"] = " ".join(rel)
        elif attrs.get("target") == "_blank":
            del attrs["target"]

        if not external and (anchor["navigation"] or href == "#main"):
            body = re.sub(r'<span\b[^>]*>\s*[↗→]\s*</span>', '', body)
            body = body.replace("↗", "").replace("→", "").rstrip()
        else:
            arrow = "↗" if external else "→"
            if "↗" in body or "→" in body:
                body = body.replace("↗", arrow).replace("→", arrow)
            elif not re.search(r"<img\b", body, re.IGNORECASE):
                body = body.rstrip() + f' <span aria-hidden="true">{arrow}</span>'
        if external and NEW_TAB_NOTE not in body:
            body += NEW_TAB_NOTE

        opening = content[anchor["start"]:anchor["body_start"]]
        if attrs != anchor["attrs"]:
            serialized = " ".join(
                key if value is None else f'{key}="{escape(value, quote=True)}"'
                for key, value in attrs.items()
            )
            opening = f"<a {serialized}>"
        if attrs != anchor["attrs"] or body != original_body:
            replacements.append((anchor["start"], anchor["body_end"], opening + body))
    for start, end, replacement in sorted(replacements, reverse=True):
        content = content[:start] + replacement + content[end:]
    return content
