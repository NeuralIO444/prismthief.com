# prismthief.com

Portfolio site for **Prism Thief** — Los Angeles street photography by Matt Ciaglia.

Plain static HTML/CSS/JS, no build step, hosted on GitHub Pages.

- `index.html` — the whole site (hero, gallery, about, exhibitions, zine, contact)
- `styles.css` / `script.js` — styling and the gallery lightbox
- `images/` — JPG masters + WebP versions (the page serves WebP where supported)
- `404.html`, `robots.txt`, `sitemap.xml` — the usual plumbing

While the prismthief.com domain is in transit, the site is served at the
project URL (no `CNAME` file). When the domain's DNS points at GitHub Pages,
re-add the `CNAME` file containing `prismthief.com` and enable
"Enforce HTTPS" in the repo's Pages settings.
