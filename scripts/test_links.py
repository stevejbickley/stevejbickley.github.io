"""Check navigation, external-tab safety and link markup preservation."""
import unittest

from links import normalize_site_links


class SiteLinkTests(unittest.TestCase):
    def test_external_link_keeps_its_markup_and_existing_relationships(self):
        source = (
            '<a href="https://example.org/paper?a=1&amp;b=2" rel="nofollow" '
            'title="Read A &gt; B"><strong>Research &amp; evidence</strong> →</a>'
        )
        result = normalize_site_links(source)
        self.assertIn('href="https://example.org/paper?a=1&amp;b=2"', result)
        self.assertIn('title="Read A &gt; B"', result)
        self.assertIn('rel="nofollow noopener"', result)
        self.assertIn('target="_blank"', result)
        self.assertIn('<strong>Research &amp; evidence</strong> ↗', result)
        self.assertIn('(opens in a new tab)', result)
        self.assertEqual(normalize_site_links(result), result)

    def test_internal_navigation_and_email_stay_in_the_same_context(self):
        source = (
            '<nav><a href="about.html">About &amp; contact</a></nav>'
            '<div class="page-jumps"><a href="#methods">Methods</a></div>'
            '<a class="brand" href="index.html">Steve</a>'
            '<a href="#main">Back to top ↑</a>'
            '<a href="mailto:steve@example.org">Email</a>'
        )
        self.assertEqual(normalize_site_links(source), source)
        self.assertEqual(
            normalize_site_links('<a href="research.html">Research ↗</a>'),
            '<a href="research.html">Research →</a>',
        )

    def test_absolute_internal_and_protocol_relative_external_links(self):
        internal = normalize_site_links(
            '<a href="https://stevejbickley.github.io/projects.html" target="_blank">Projects ↗</a>'
        )
        self.assertNotIn('target=', internal)
        self.assertIn('Projects →', internal)
        external = normalize_site_links('<a href="//osf.io/g96uw/">OSF</a>')
        self.assertIn('target="_blank"', external)
        self.assertIn('aria-hidden="true">↗</span>', external)

    def test_gallery_templates_and_scripts_are_preserved(self):
        metadata = '<script type="application/ld+json">{"text":"<a href=\"https://example.org\">"}</script>'
        source = metadata + (
            '<template><figcaption><a href="https://doi.org/10/example">Thesis ↗</a>'
            '</figcaption></template><a class="photo-link" href="assets/photo.webp">'
            '<img src="assets/photo.webp" alt="A photograph"></a>'
        )
        result = normalize_site_links(source)
        self.assertTrue(result.startswith(metadata))
        self.assertIn('href="https://doi.org/10/example" target="_blank" rel="noopener"', result)
        self.assertIn('<a class="photo-link" href="assets/photo.webp"><img', result)
        self.assertEqual(normalize_site_links(result), result)


if __name__ == "__main__":
    unittest.main()
