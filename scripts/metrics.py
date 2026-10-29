"""Validated public metric snapshots, rendered into static HTML at build time."""
from datetime import date
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

AGENT = "SteveBickleyWebsite/1.0 (+https://stevejbickley.github.io/)"
SOURCES = {
    "scholar": "https://scholar.google.com/citations?user=ARJITb8AAAAJ&hl=en",
    "ai-economics": "https://link.springer.com/article/10.1007/s11192-022-04294-w",
    "ai-ethics": "https://link.springer.com/article/10.1007/s00146-022-01452-9",
}


class Text(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.parts = []
        self.feed(content)

    def handle_data(self, data):
        self.parts.append(data)

    def plain(self):
        return " ".join(" ".join(self.parts).split())


def parse_scholar(content):
    name = re.search(r'id=["\']gsc_prf_in["\'][^>]*>(.*?)</', content, re.S)
    if not name or Text(name[1]).plain() != "Steve Bickley" or "qut.edu.au" not in content:
        raise ValueError("The expected author profile was not returned")
    cells = re.findall(r'class=["\']gsc_rsb_std["\'][^>]*>(.*?)</td>', content, re.S)
    if len(cells) != 6:
        raise ValueError("Citation table missing or changed")
    values = [Text(cell).plain().replace(",", "") for cell in cells]
    if not all(value.isdigit() for value in values):
        raise ValueError("Citation table contains non-numeric values")
    citations, h_index = int(values[0]), int(values[2])
    if not 0 <= h_index <= citations <= 10_000_000:
        raise ValueError("Citation values outside expected bounds")
    return {"citations": citations, "h_index": h_index}


def parse_publisher(content, doi):
    if doi.lower() not in content.lower() or "Bickley" not in content:
        raise ValueError("The expected article was not returned")
    paragraphs = re.findall(
        r'<p\b[^>]*class=["\'][^"\']*app-article-metrics-bar__count[^"\']*["\'][^>]*>(.*?)</p>',
        content, re.S,
    )
    text = " ".join(Text(paragraph).plain() for paragraph in paragraphs)
    accesses = re.search(r"\b(\d[\d,]*(?:\.\d+)?\s*[kKmM]?)\s+Accesses\b", text)
    attention = re.search(r"\b(\d+)\s+Altmetric\b", text)
    if not accesses or not attention:
        raise ValueError("Publisher counters missing or changed")
    return {"accesses": accesses[1].replace(" ", ""), "altmetric": int(attention[1])}


def robots_allow(content, url):
    """Apply the most specific matching robots rule, including * and $ patterns."""
    groups, agents, rules = [], [], []
    for raw in content.splitlines() + ["User-agent: __end__"]:
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        field, value = (part.strip() for part in line.split(":", 1))
        if field.lower() == "user-agent":
            if rules:
                groups.append((agents, rules)); agents, rules = [], []
            agents.append(value.lower())
        elif field.lower() in ("allow", "disallow") and agents and value:
            rules.append((field.lower(), value))
    product = AGENT.split("/", 1)[0].lower()
    matching = [(max((len(a) for a in agents if a != "*" and a in product), default=0), agents, rules)
                for agents, rules in groups if "*" in agents or any(a in product for a in agents)]
    if not matching:
        return True
    specificity = max(group[0] for group in matching)
    target = urlsplit(url).path + ("?" + urlsplit(url).query if urlsplit(url).query else "")
    matches = []
    for score, _, rules in matching:
        if score != specificity:
            continue
        for kind, pattern in rules:
            expression = re.escape(pattern).replace(r"\*", ".*")
            expression = expression[:-2] + "$" if expression.endswith(r"\$") else expression
            if re.match(expression, target):
                matches.append((len(pattern.replace("*", "").rstrip("$")), kind == "allow"))
    return max(matches)[1] if matches else True


def fetch(url):
    # Use the same plain HTTPS client on macOS and the GitHub-hosted runner.
    # No cookies, credentials, proxy rotation or challenge-solving are used.
    try:
        response = subprocess.run(
            ["curl", "--fail", "--silent", "--show-error", "--location", "--max-time", "20", "--user-agent", AGENT, url],
            capture_output=True, timeout=25,
        )
    except subprocess.TimeoutExpired as error:
        raise OSError("Public request timed out") from error
    if response.returncode:
        raise OSError(f"Public request failed (curl exit {response.returncode})")
    if len(response.stdout) > 2_000_000:
        raise ValueError("Response exceeds the expected size")
    return response.stdout.decode("utf-8")


def refresh(data, fetcher=fetch, today=None):
    today = today or date.today().isoformat()
    rules, successes, failures = {}, [], []
    for source, url in SOURCES.items():
        try:
            host = urlsplit(url).netloc
            if host not in rules:
                rules[host] = fetcher(f"https://{host}/robots.txt")
            if not robots_allow(rules[host], url):
                raise ValueError("Public access rules do not allow this request")
            content = fetcher(url)
            values = parse_scholar(content) if source == "scholar" else parse_publisher(content, url.split("/article/", 1)[1])
            data[source] = {"values": values, "checked_at": today, "source": url, "mode": "automatic"}
            successes.append(source)
        except (OSError, ValueError, UnicodeError) as error:
            # Preserve both the previous values and their genuine observation date.
            failures.append((source, str(error)))
    return successes, failures


def render_metrics(content, data):
    def value(match):
        source, field = match[1].rsplit(".", 1)
        number = data[source]["values"][field]
        display = f"{number:,}" if isinstance(number, int) else str(number)
        return f'<span data-metric="{match[1]}">{escape(display)}</span>'

    def timestamp(match):
        source = match[1]
        stored = data[source]["checked_at"]
        # Manual snapshots may only be precise to a month.
        parsed = date.fromisoformat(stored + "-01" if len(stored) == 7 else stored)
        display = parsed.strftime("%B %Y") if len(stored) == 7 else f"{parsed.day} {parsed:%B %Y}"
        return f'<time data-metric-date="{source}" datetime="{stored}">{display}</time>'

    content = re.sub(r'<span data-metric="([a-z0-9_.-]+)">[^<]*</span>', value, content)
    return re.sub(r'<time data-metric-date="([a-z0-9_-]+)"[^>]*>[^<]*</time>', timestamp, content)


def load_metrics(root):
    path = Path(root) / "data/research-metrics.json"
    return json.loads(path.read_text()) if path.exists() else None
