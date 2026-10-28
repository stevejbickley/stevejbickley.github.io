# Steve Bickley — personal academic website starter

This package contains **six complete, editable page drafts**. It includes both Quarto `.qmd` source files and a compiled static site in the `docs/` folder. The compiled HTML can be hosted directly with GitHub Pages without Quarto.

## Files

- `index.qmd` — Home
- `research.qmd` — Research
- `publications.qmd` — all 12 peer-reviewed journal articles, five book/encyclopedia entries and five commissioned/technical reports (as in October 2026 CV)
- `teaching.qmd` — teaching and supervision
- `projects.qmd` — public research, Panalogy Lab and engineering projects
- `about.qmd` — biography, qualifications, contact links
- `_quarto.yml` — optional Quarto site configuration
- `assets/styles.css` — custom styling
- `docs/` — ready-to-host HTML website

## IMPORTANT: Before publishing

1. **Review outside-work and conflict-of-interest disclosures and approvals at QUT**, including any Panalogy Lab company-officer role, before publishing this draft. Public biography text is not a substitute for required institutional disclosures.
2. Confirm permission to publicly refer to client and research-project work, names, findings and technology details. No confidential reports or files are included.
3. Verify all affiliations, titles, status dates and bibliographic details (especially the 2026 World Scientific book chapter collection title).
4. Optionally replace the textual hero with a photo you own/have permission to use. Do not automatically copy a QUT-hosted portrait without checking licence/permission.
5. Add a separate public CV if desired. Avoid attaching the original unredacted CV with phone numbers, referees, grant applications or sensitive project details.
6. If a business interest is undeclared, sort out any disclosure/approval obligations first; omitting it from this website does not remove those obligations.

## Quickest deployment: GitHub Pages

1. Create a **public** GitHub repository named `stevejbickley.github.io` (for the username site), if available on your account.
2. Upload the **contents of this package**, keeping the `docs/` directory at the repository root. Do not upload the outer folder as an extra nested directory.
3. In repository **Settings → Pages**, choose **Deploy from a branch** → `main` → `/docs` and save.
4. Your website should become available at `https://stevejbickley.github.io/` after GitHub Pages deploys.
5. Update the `.qmd` source pages as needed. To regenerate `docs/` using Quarto, install Quarto and run `quarto render` in the repository root. Commit the updated `docs/` files.

If you instead use another repository name, the website URL will include a repository suffix. The generated pages' internal links are relative so they work in either case.

## Quarto alternative

1. Install Quarto (https://quarto.org/docs/get-started/).
2. Open this project directory in VS Code or RStudio.
3. Run `quarto preview` locally and `quarto render` to update compiled HTML.
4. Publish from `docs/` in GitHub Pages. See https://quarto.org/docs/publishing/github-pages.html.

## Google Sites alternative

If you prefer Google Sites, copy the content of each `.qmd` file (excluding the first YAML front matter block) into the matching page. Apply your chosen site theme and manually add navigation; GitHub Pages and Quarto files are not necessary.

## Domain and maintenance

A custom domain can be configured later through GitHub Pages and your DNS provider. Do **not** put an unregistered or unverified domain into the `CNAME` configuration. Update publications, projects, roles and site links periodically. The draft deliberately avoids auto-changing claims and unverified commercial metrics.
