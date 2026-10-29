import copy
import json
from pathlib import Path
import tempfile
import unittest

from metrics import SOURCES, parse_publisher, parse_scholar, refresh, render_metrics, robots_allow
from finalize import finalize_site

SCHOLAR = '<div id="gsc_prf_in">Steve Bickley</div><div>Verified email at qut.edu.au</div>' + ''.join(
    f'<td class="gsc_rsb_std">{value}</td>' for value in ["738", "733", "9", "9", "9", "9"]
)


def article(doi):
    return f'<meta content="{doi}">Bickley<p class="app-article-metrics-bar__count"><svg></svg>53k <span>Accesses</span></p><p class="app-article-metrics-bar__count">16 <span>Altmetric</span></p>'


class MetricTests(unittest.TestCase):
    def test_profile_identity_and_table_are_required(self):
        self.assertEqual(parse_scholar(SCHOLAR), {"citations": 738, "h_index": 9})
        for bad in ("<p>Verify you are human</p>", SCHOLAR.replace("Steve Bickley", "Another Author"), SCHOLAR.replace(">738<", ">Unavailable<")):
            with self.assertRaises(ValueError):
                parse_scholar(bad)

    def test_publisher_counters_and_article_identity(self):
        doi = "10.1007/s11192-022-04294-w"
        self.assertEqual(parse_publisher(article(doi), doi), {"accesses": "53k", "altmetric": 16})
        with self.assertRaises(ValueError):
            parse_publisher(article(doi), "10.1007/wrong-article")
        with self.assertRaises(ValueError):
            parse_publisher(article(doi).replace("Accesses", "Unavailable"), doi)

    def test_robots_most_specific_allow_and_restrictions(self):
        rules = 'User-agent: *\nDisallow: /citations?\nAllow: /citations?user=\nDisallow: /citations?*cstart=\n'
        self.assertTrue(robots_allow(rules, SOURCES["scholar"]))
        self.assertFalse(robots_allow(rules, SOURCES["scholar"] + "&cstart=100"))
        publisher = 'User-agent: *\nDisallow: /\nAllow: /article/\nDisallow: /*/metrics\nDisallow: /*/*/metrics\n'
        self.assertTrue(robots_allow(publisher, SOURCES["ai-economics"]))
        self.assertFalse(robots_allow(publisher, SOURCES["ai-economics"] + "/metrics"))

    def test_failed_source_keeps_its_values_and_original_date(self):
        data = {"scholar": {"values": {"citations": 730, "h_index": 9}, "checked_at": "2026-10-01"},
                "conversation": {"values": {"reads": 3962}, "checked_at": "2026-08-05"}}
        previous = copy.deepcopy(data)

        def offline(url):
            raise OSError("Unavailable")

        successes, failures = refresh(data, offline, today="2026-10-29")
        self.assertEqual(successes, [])
        self.assertEqual(len(failures), 3)
        self.assertEqual(data, previous)

    def test_partial_refresh_does_not_relabel_stale_or_manual_data(self):
        data = {"ai-economics": {"values": {"accesses": "50k", "altmetric": 15}, "checked_at": "2026-08-01"},
                "scival": {"values": {"fwci": "4.70"}, "checked_at": "2026-02"}}
        old_economics = copy.deepcopy(data["ai-economics"])

        def public(url):
            if url.endswith("robots.txt"):
                return "User-agent: *\nAllow: /"
            if url == SOURCES["scholar"]:
                return SCHOLAR
            raise OSError("Unavailable")

        successes, failures = refresh(data, public, today="2026-10-29")
        self.assertEqual(successes, ["scholar"])
        self.assertEqual(len(failures), 2)
        self.assertEqual(data["scholar"]["checked_at"], "2026-10-29")
        self.assertEqual(data["ai-economics"], old_economics)
        self.assertEqual(data["scival"]["checked_at"], "2026-02")

    def test_static_render_is_consistent_and_idempotent(self):
        data = {"conversation": {"values": {"reads": 3962}, "checked_at": "2026-08-05"}}
        html = '<strong><span data-metric="conversation.reads">0</span></strong> · <time data-metric-date="conversation" datetime="2020-01-01">Old date</time>'
        rendered = render_metrics(html, data)
        self.assertIn('>3,962</span>', rendered)
        self.assertIn('datetime="2026-08-05">5 August 2026</time>', rendered)
        self.assertEqual(render_metrics(rendered, data), rendered)

    def test_one_snapshot_updates_every_built_page_without_javascript(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ("assets", "docs", "data"):
                (root / folder).mkdir()
            (root / "assets/styles.css").write_text("body { color: green; }")
            (root / "assets/site.js").write_text("")
            source = '<html><span data-metric="conversation.reads">0</span><time data-metric-date="conversation">Old</time></html>'
            for name in ("index.html", "publications.html"):
                (root / "docs" / name).write_text(source)
            data = {"conversation": {"values": {"reads": 3962}, "checked_at": "2026-08-05"}}
            (root / "data/research-metrics.json").write_text(json.dumps(data))
            finalize_site(root)
            for page in (root / "docs").glob("*.html"):
                self.assertIn('>3,962</span>', page.read_text())
                self.assertIn('>5 August 2026</time>', page.read_text())


if __name__ == "__main__":
    unittest.main()
