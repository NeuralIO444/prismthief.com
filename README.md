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

## Adding photos (the pipeline)

1. Upload a JPG into the `photos/` folder (GitHub app or web both work).
2. GitHub Actions runs `tools/build_gallery.py`: the photo is resized
   (max 1600px), WebP + JPG versions land in `images/`, camera EXIF
   (model · aperture · shutter · ISO) is added under the caption, and the
   gallery in `index.html` rebuilds itself. Live in about a minute.
3. Titles come from `gallery.json` in the repo root — new photos get a
   title from their filename; edit that file to rename or reorder.
4. Delete a photo from `photos/` and it disappears from the gallery.

Photos exported through Lightroom/Instagram usually have EXIF stripped,
so the camera line only appears for files dropped straight from a camera
or phone.
