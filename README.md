# Steve Bickley — personal academic website

A six-page, responsive website built with Quarto and published as static HTML from `docs/` on GitHub Pages. It uses a shared HTML template, CSS and a small vanilla JavaScript file; there is no npm dependency or application server.

## Build and preview

Requires Quarto, Python 3 and Git. Run the commands below from the repository root (the folder containing `_quarto.yml`). Check that the tools are available:

```sh
quarto --version
python3 --version
git --version
```

### 1. Start with the latest version

```sh
git status
git pull --ff-only
```

Review any existing local changes first. The weekly metrics workflow can update the remote repository between editing sessions. Save or commit your current work before pulling if Git reports that it would be overwritten.

### 2. Edit the source files

Use the file map in **Where to edit** below. Most content is HTML inside the fenced raw-HTML block in each `.qmd` file. Keep the opening and closing fences intact. For example, a normal paragraph is `<p>Text here.</p>`, a link is `<a href="https://example.com">Link text</a>`, and a dropdown uses `<details><summary>Label</summary>…</details>`. Use `&amp;` for an ampersand in HTML.

Edit the `.qmd` files and the original files in `assets/`. The HTML in `docs/` and the fingerprinted files in `assets/generated/` are build output and will be overwritten on the next render.

### 3. Build the complete site

```sh
quarto render
```

This rebuilds all six pages into `docs/` and runs `scripts/finalize.py` automatically. The finalizer preserves standards-mode HTML with older Quarto versions, creates the `.nojekyll` marker, inserts stored metrics, applies the link conventions below and gives CSS/JavaScript content-based filenames. Commit the updated files in **both** `assets/generated/` and `docs/assets/generated/` along with the sources and `docs/` output. Older asset versions are retained so visitors with cached HTML can still load its matching styles and scripts.

For template, CSS or JavaScript changes, always render the complete site so every page uses the same version. A normal build does not fetch new metrics; see **Automatic metric snapshots** for an optional manual refresh.

### 4. Preview the built pages

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory docs
```

Open [the local preview](http://127.0.0.1:8765/). Keep that terminal running; press **Ctrl+C** to stop it. To make further changes while it is running, edit and run `quarto render` in a second terminal, then reload the browser. This preview serves the same static files that GitHub Pages publishes.

Check the edited pages at desktop and narrow phone widths. For relevant changes, check navigation, publication search/filters, dropdowns, image links and the CMM gallery on Home and Research. The gallery supports Previous/Next, keyboard arrows and Escape; closing it returns focus to the image link.

If port 8765 is already in use, stop the earlier preview or run `python3 -m http.server 8766 --bind 127.0.0.1 --directory docs` and open `http://127.0.0.1:8766/`.

### 5. Check and publish

Run the existing link, cache and metric regression checks and review the changes:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
git diff --check
git status
git diff --stat
```

When the preview is ready, stage the source and generated output together, review the staged changes, commit and push:

```sh
git add -A
git diff --cached --stat
git diff --cached
git commit -m "Update website content"
git push origin main
```

`git add -A` stages all local changes, so check that the staged files belong to the intended update. In GitHub, open **Actions → pages build and deployment** and wait for success, then check [the live site](https://stevejbickley.github.io/). Pages serves **main → /docs**; pushing source edits without rebuilding `docs/` will not update the public page content. The Markdown README is repository documentation and does not become an extra website page.

If a push is rejected because the remote branch has advanced, commit your local work, run `git pull --rebase`, resolve any conflicts, rebuild and review the generated output before pushing again. If that rebuild changes tracked files, commit those changes too. The GitHub Actions metrics update is a common reason for the remote branch to advance.

### Troubleshooting

- **The site looks unchanged:** confirm `quarto render` completed, that generated `docs/` files were committed, and that the Pages deployment succeeded. Reload the page. New CSS/JS filenames should appear in the generated HTML after those assets change.
- **The preview looks unstyled:** serve `docs/` with the command above rather than opening a `.qmd` file or the source directory. Run a complete render if a generated asset is missing.
- **A table inside a dropdown is malformed:** preserve `data-quarto-disable-processing="true"` on the existing feedback and engineering tables; older Quarto versions otherwise reprocess their HTML.
- **A render removes `docs/.DS_Store`:** this is an existing tracked macOS metadata file, not website content. Exclude that incidental deletion from a content-only commit with `git restore -- docs/.DS_Store`.

### Google Search Console verification

`google3fa7ceb2f0784351.html` is the original Google verification file. Keep it in the repository root; `_quarto.yml` lists it as a resource so every build copies it unchanged to `docs/`, the folder GitHub Pages publishes. The finalizer leaves Google verification HTML files untouched. The public URL is [google3fa7ceb2f0784351.html](https://stevejbickley.github.io/google3fa7ceb2f0784351.html). Keep this file in place after verification. If Google issues a replacement, save the original file without editing its contents, update the resource filename in `_quarto.yml`, rebuild and publish.


## Automatic metric snapshots

The `Refresh research metrics` GitHub Actions workflow runs weekly (Monday, 06:23 Brisbane time) and can also be run manually from Actions. It uses Python 3 and curl (both included on the hosted runner) to check the public Google Scholar profile and two Springer Nature article landing pages, validates the returned author/article and counters, and saves successful observations in `data/research-metrics.json`. It respects public access rules and makes no attempt to bypass a challenge or access restriction. The counters are best-effort public-page integrations, not guaranteed APIs: a blocked request or changed page retains its previous value **and original observation date**. A fully failed refresh fails the workflow without changing the data.

The finalizer inserts the stored values into all marked locations in the generated HTML. Visitors make no extra API requests and need no JavaScript to see the metrics. The scheduled workflow commits refreshed snapshots and explicitly requests a Pages rebuild, because commits using `GITHUB_TOKEN` do not trigger Pages by themselves. It needs repository `contents: write` and `pages: write`; it does not change the existing Pages source setting.

SciVal and The Conversation readership remain explicitly dated snapshots. They are not labelled live: SciVal requires entitled institutional API access, and article readership is an author analytics record. Their data is centralised in the same JSON so an authorised export can update all page locations together. Historical rankings remain tied to their original reporting periods. No credentials, private dashboards or source documents are published.

For a manual public refresh, run `python3 scripts/update_metrics.py`, then `quarto render`. For a local render using the current stored observations, run `quarto render` alone.

## Where to edit

- `index.qmd` — introduction, portrait, selected work, research themes, the CMM and public writing.
- `research.qmd` — current research themes, methods (with optional CMM and feedback figures), sourced impact metrics, policy engagement and collaborations.
- `publications.qmd` — research outputs with search and type filters, plus a separate public-writing section. The October 2026 record has 31 outputs.
- `projects.qmd` — research, software, Panalogy Lab and engineering project details.
- `teaching.qmd` — teaching evidence, open resources, supervision, Nudgeathon mentoring, invited speaking and conference presentations.
- `about.qmd` — biography, engineering portrait, experience, international study, recognition and contact.
- `assets/page.html` — shared navigation, metadata, footer, image-dialog controls and the inert CMM gallery metadata for Figures 2–4. The homepage-only `application/ld+json` script contains the `ProfilePage` / `Person` structured data; edit the preferred name, aliases, description and `sameAs` profile links here, then rebuild the complete site. Keep `#person` as the stable identity identifier.
- `assets/styles.css` — colours, type, layouts and responsive breakpoints.
- `assets/site.js` — accessible mobile navigation, publication filters and the single-image/CMM gallery viewer.
- `scripts/links.py` — build-time link conventions: internal content links use →, external web links use ↗ and open a new tab with `rel="noopener"` and a screen-reader announcement. Menus, page-jump navigation, email links and image-only enlargement controls keep their own presentation; Back to top keeps ↑. Photo enlargement uses ⤢, and the full-resolution image viewer retains its separate tab.
- `assets/images/` — optimised photographs, event photos in `assets/images/events/` and thesis figure crops in `assets/images/research/`. Larger images are available through the image viewer.

Page content is HTML inside Quarto raw-HTML blocks, so the layouts remain reproducible through `quarto render`. Edit the sources rather than the generated HTML. Main navigation remains available without JavaScript; publication entries are all visible when scripting is disabled. Research figures and event photos link directly to larger images without JavaScript; with JavaScript they open in a keyboard-accessible native dialog.

Add normal `<a href="…">Label</a>` links when editing content. The build classifies relative links and URLs on `stevejbickley.github.io` as internal, and HTTP(S) links to other hosts as external. It adds or corrects the direction indicator, target and accessible new-tab note automatically, including in the CMM gallery's captions. Public-writing article titles suppress the visible arrow through CSS while retaining external-link behaviour. These conventions work without JavaScript; leave email links as `mailto:` links. The shared footer's Elsewhere profiles, including OSF, are edited in `assets/page.html`.

## Content, images and source records

The October 2026 CVs were used as factual reference material. Original private CVs, referee details, personal telephone numbers and private email addresses are not included. Current positions and dated achievements should be reviewed as they change. Research applications with managed access are described without linking visitors to restricted systems.

All thirteen supplied photographs are included: portraits and the SEAMEO RETRAC panel, Nudgeathon 2018 and 2026, Nyrstar Port Pirie, Something Tech 2023 and WASAA 2020. Captions and descriptive alternative text are kept beside each image in its `.qmd` source. WebP derivatives strip original metadata, preserve the event photographs’ full frames and provide responsive sizes without upscaling the source files. The Something Tech booth image identifies Benno Torgler, Steve Bickley and Ho Fai Chan from left to right; the Port Pirie image includes designer Glen Starkey.

When replacing a photograph, update its `src`, `srcset`, `width`, `height`, `alt` and caption together. Every `srcset` width must match the actual pixel width of that file. Keep original private photographs and their metadata outside the published assets.

The design uses system sans-serif fonts and Georgia, so it does not depend on third-party font services or analytics. Academic research, independent Panalogy Lab work and prior engineering employment are identified in the content.

Research figures are original crops from the 2023 QUT thesis, [Bridging Complexity and Behavioural Economics: The Constrained Methods Matrix](https://doi.org/10.5204/thesis.eprints.244769). Their labels, arrows, shading and data are retained; nothing is redrawn. Original thesis, seminar and grant files are not copied into the public website.

| Asset in `assets/images/research/` | Thesis figure | Printed page | PDF page |
| --- | --- | --- | --- |
| `cmm-matrix` | Figure 1: extended CMM | 13 | 34 |
| `cmm-data-and-assumptions` | Figure 2: movement through the matrix | 18 | 39 |
| `cmm-emerging-methods` | Figure 3: methods and emerging challenges | 20 | 41 |
| `cmm-chapter-mapping` | Figure 4: mapping Chapter 2 | 22 | 43 |
| `nested-feedback` | Figure 5: hierarchical feedback | 56 | 77 |
| `ai-economics-growth` | Figure 31: historical growth of AI papers | 334 | 355 |
| `ai-economics-networks` | Figure 34: JEL subject networks | 342 | 363 |

The CMM is credited to the thesis and Bickley & Torgler (2023), building on Minsky, Sloman and Singh. The feedback discussion draws on Simon (1962) and Ceddia et al. (2013). The two historical AI-economics plots remain in the asset folder but are no longer displayed on Research.

Home and Research each display one CMM thumbnail. Its link uses `data-figure-gallery="cmm"`; the remaining figures, dimensions, alternative text and captions are in the `#cmm-gallery` template in `assets/page.html`. Template images use `data-src` so the full-size files load only when selected. To change Figure 1's caption, edit it on both pages; edit Figures 2–4 in the shared template. Ordinary photos and the feedback diagram remain single-image views.

The research page keeps aggregate citation figures and lists all 12 peer-reviewed journal venues in an unlinked, semicolon-separated paragraph. `data/journal-rankings-2025.json` records the manual 2025 SJR/best-quartile snapshot and the exact publisher/university source URLs. Update the matching paragraph in `research.qmd` when changing that snapshot; it is not automatically rendered from the JSON. SJR scores and subject quartiles are journal-level indicators, distinct from article citations and Clarivate Journal Impact Factors. SCImago remains linked for exploration. The two Springer article snapshots remain in the metric archive, although their article-specific cards have been removed.

`data/bita-publications.json` records the seven added BITA working/policy paper citations and their PDF URLs. It is a provenance record; displayed entries are edited in `publications.qmd`. Working Paper 10 uses its documented May 2025 publication date despite a 2024 PDF copyright notice. The publication count in the sidebar is manual; the search/filter count is calculated from the entries. Other dated content, including SurveyLM registrations, donations and hosting credits, is edited directly in `projects.qmd` with its observation date and currency.

The full engineering portfolio is available in a closed disclosure on Projects (26 engagements). Project credits distinguish leadership, software development, supervision and partner support. SurveyLM's institutional affiliations describe registrations or use by researchers, and ongoing evaluations remain labelled as such. AWS Activate credits are non-cash US-dollar support, separate from Australian-dollar user donations and commissioned QUT/ARC BITA research. Industrial results retain their field-report/partner-reported attribution.

Teaching feedback sits directly below each unit description and retains all five substantive comments and all rating categories from the QUT Student Voice Survey export dated 26 June 2026. EFB350 (Semester 1, 2024) has 3 respondents: 2 strongly agree and 1 agree. EFN405 (Semester 1, 2023) has 6: 3 strongly agree, 2 agree and 1 neutral. The 9% response rate is combined across the two units, not an individual unit rate. Preserve the sample sizes, period, anonymous wording and source date when editing. The private dashboard is not published.

Supervision figures distinguish appointments from unique people and upcoming intakes from completed supervision. Student demographic categories are aggregate and overlapping. Nudgeathon 2022 identifies Steve as both competitor and PhD mentor on the first-place team; 2017 also records his competitor role. Institutional visits are described as visits rather than formal partnerships.

About includes all 14 reviewing journals/platforms from the October 2026 CV and an invitation for board/advisory enquiries. Research media coverage uses selected linked articles, the full CV outlet record and grouped historical translations/republications. The Wikipedia citation opens a recorded historical revision. Authored public writing is listed separately on Publications. Article titles and source links are kept with their displayed entries; the former standalone photo/research/teaching notes have been consolidated here, with their earlier history retained in Git.
