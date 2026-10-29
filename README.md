# Steve Bickley — personal academic website

A six-page, responsive website built with Quarto and published as static HTML from `docs/` on GitHub Pages. It uses a shared HTML template, CSS and a small vanilla JavaScript file; there is no npm dependency or application server.

## Build and preview

Requires Quarto and Python 3. From the repository root:

```sh
quarto render
python3 -m http.server 8765 --bind 127.0.0.1 --directory docs
```

Open `http://127.0.0.1:8765/`. Commit the edited sources and generated `docs/` output together when publishing. GitHub Pages should serve the `main` branch's `/docs` directory.

`scripts/finalize.py` runs automatically after Quarto rendering. It preserves standards-mode HTML with older Quarto versions, creates the `.nojekyll` marker and gives CSS and JavaScript content-based filenames. Every published page references these fingerprinted assets, preventing an older cached stylesheet from being applied to new HTML. The generated files live in `assets/generated/` and `docs/assets/generated/`; commit both with the build. Older versions are retained for visitors with cached HTML. Edit `assets/styles.css` and `assets/site.js`, then render; do not edit the fingerprinted copies.

Run the cache and metric regression checks with `python3 -m unittest discover -s scripts -p 'test_*.py'`.

## Automatic metric snapshots

The `Refresh research metrics` GitHub Actions workflow runs weekly (Monday, 06:23 Brisbane time) and can also be run manually from Actions. It uses Python 3 and curl (both included on the hosted runner) to check the public Google Scholar profile and two Springer Nature article landing pages, validates the returned author/article and counters, and saves successful observations in `data/research-metrics.json`. It respects public access rules and makes no attempt to bypass a challenge or access restriction. The counters are best-effort public-page integrations, not guaranteed APIs: a blocked request or changed page retains its previous value **and original observation date**. A fully failed refresh fails the workflow without changing the data.

The finalizer inserts the stored values into all marked locations in the generated HTML. Visitors make no extra API requests and need no JavaScript to see the metrics. The scheduled workflow commits refreshed snapshots and explicitly requests a Pages rebuild, because commits using `GITHUB_TOKEN` do not trigger Pages by themselves. It needs repository `contents: write` and `pages: write`; it does not change the existing Pages source setting.

SciVal and The Conversation readership remain explicitly dated snapshots. They are not labelled live: SciVal requires entitled institutional API access, and article readership is an author analytics record. Their data is centralised in the same JSON so an authorised export can update all page locations together. Historical rankings remain tied to their original reporting periods. No credentials, private dashboards or source documents are published.

For a manual public refresh, run `python3 scripts/update_metrics.py`, then `quarto render`. For a local render using the current stored observations, run `quarto render` alone.

## Where to edit

- `index.qmd` — introduction, portrait, selected work, research themes, the CMM and public writing.
- `research.qmd` — current research themes, methods (with optional CMM and feedback figures), sourced impact metrics, policy engagement and collaborations.
- `publications.qmd` — 27 research outputs with search and type filters.
- `projects.qmd` — research, software, Panalogy Lab and engineering project details.
- `teaching.qmd` — teaching evidence, open resources, supervision, Nudgeathon mentoring, invited speaking and conference presentations.
- `about.qmd` — biography, engineering portrait, experience, international study, recognition and contact.
- `assets/page.html` — shared navigation, metadata and footer.
- `assets/styles.css` — colours, type, layouts and responsive breakpoints.
- `assets/site.js` — accessible mobile navigation, publication filters and the image viewer.
- `assets/images/` — optimised photographs, event photos in `assets/images/events/` and thesis figure crops in `assets/images/research/`. Larger images are available through the image viewer.

Page content is HTML inside Quarto raw-HTML blocks, so the layouts remain reproducible through `quarto render`. Edit the sources rather than the generated HTML. Main navigation remains available without JavaScript; publication entries are all visible when scripting is disabled. Research figures and event photos link directly to larger images without JavaScript; with JavaScript they open in a keyboard-accessible native dialog.

## Content and photos

The October 2026 CVs were used as factual reference material. Original private CVs, referee details, personal telephone numbers and private email addresses are not included. Current positions and dated achievements should be reviewed as they change. Research applications with managed access are described without linking visitors to restricted systems.

All thirteen supplied photographs are included: the portraits and SEAMEO RETRAC panel, Nudgeathon 2018 and 2026, Nyrstar Port Pirie, Something Tech 2023 and WASAA 2020. Placements and caption context are recorded in `PHOTO-NOTES.md`. WebP derivatives strip original metadata, preserve the event photographs’ full frames and provide responsive sizes without upscaling the source files.

The design uses system sans-serif fonts and Georgia, so it does not depend on third-party font services or analytics. Academic research, independent Panalogy Lab work and prior engineering employment are identified in the content.

Research figures and metric dates are documented in `RESEARCH-NOTES.md`. Original thesis, seminar and grant files are not copied into the public website.
