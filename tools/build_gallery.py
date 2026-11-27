#!/usr/bin/env python3
"""Prism Thief gallery pipeline.

Drop JPGs into photos/ and this script rebuilds the site's gallery:
  - resizes each photo to at most 1600px wide
  - writes images/<slug>.jpg + images/<slug>.webp
  - pulls camera EXIF (model, aperture, shutter, ISO) into the caption
  - regenerates the gallery block in index.html between the GALLERY markers
  - removes outputs for photos no longer in photos/

Titles live in gallery.json (repo root), keyed by slug, and survive rebuilds.
New photos get a title from their filename; edit gallery.json to rename.
Runs locally and in GitHub Actions (.github/workflows/gallery.yml).
"""
import html
import json
import os
import re
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTOS = os.path.join(ROOT, "photos")
IMAGES = os.path.join(ROOT, "images")
DATA = os.path.join(ROOT, "gallery.json")
INDEX = os.path.join(ROOT, "index.html")
PROTECTED = {"after-hours", "avatar"}  # hero + avatar are not gallery photos
MAXW = 1600


def slugify(name):
    base = os.path.splitext(os.path.basename(name))[0].lower()
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-")


def title_from_slug(slug):
    return slug.replace("-", " ").title()


def exif_line(path):
    try:
        img = Image.open(path)
        ex = img.getexif()
        if not ex:
            return ""
        model = str(ex.get(272, "")).strip()
        if model.upper().startswith("RICOH"):
            model = "Ricoh" + model[5:]
        try:
            ifd = ex.get_ifd(0x8769)
        except Exception:
            ifd = {}
        parts = []
        if model:
            parts.append(model)
        fnum = ifd.get(33437)
        if fnum:
            parts.append(f"f/{float(fnum):g}")
        expo = ifd.get(33434)
        if expo:
            e = float(expo)
            parts.append(f"1/{round(1 / e)}" if 0 < e < 1 else f"{e:g}s")
        iso = ifd.get(34855)
        if iso:
            parts.append(f"ISO {iso}")
        return " · ".join(parts)
    except Exception:
        return ""


def main():
    os.makedirs(IMAGES, exist_ok=True)
    data = {"photos": []}
    if os.path.exists(DATA):
        data = json.load(open(DATA))
    known = {p["slug"]: p for p in data.get("photos", [])}

    files = sorted(
        f for f in os.listdir(PHOTOS) if f.lower().endswith((".jpg", ".jpeg"))
    )
    by_slug = {}
    for f in files:
        by_slug.setdefault(slugify(f), f)

    # Order: existing gallery.json order first, then new photos by filename.
    ordered = []
    for p in data.get("photos", []):
        if p["slug"] in by_slug and p not in ordered:
            ordered.append({"slug": p["slug"], "title": p["title"]})
    for f in files:
        s = slugify(f)
        if s not in known and all(o["slug"] != s for o in ordered):
            ordered.append({"slug": s, "title": title_from_slug(s)})

    figures = []
    live_slugs = set()
    for entry in ordered:
        slug = entry["slug"]
        src = os.path.join(PHOTOS, by_slug[slug])
        live_slugs.add(slug)
        img = Image.open(src).convert("RGB")
        if img.width > MAXW:
            img = img.resize(
                (MAXW, round(img.height * MAXW / img.width)), Image.LANCZOS
            )
        img.save(os.path.join(IMAGES, slug + ".jpg"), quality=85)
        img.save(os.path.join(IMAGES, slug + ".webp"), "WEBP", quality=82)
        exif = exif_line(src)
        small = f"<small>{html.escape(exif)}</small>" if exif else ""
        title = html.escape(entry["title"])
        figures.append(
            f'      <figure><picture><source srcset="images/{slug}.webp" type="image/webp">'
            f'<img src="images/{slug}.jpg" width="{img.width}" height="{img.height}" loading="lazy" alt="{title}"></picture>'
            f"<figcaption>{title}{small}</figcaption></figure>"
        )

    # Remove outputs for photos that left the drop folder.
    for f in os.listdir(IMAGES):
        stem, ext = os.path.splitext(f)
        if ext.lower() in (".jpg", ".webp") and stem not in live_slugs | PROTECTED:
            os.remove(os.path.join(IMAGES, f))

    # Regenerate the gallery block.
    page = open(INDEX).read()
    block = "<!-- GALLERY:START -->\n" + "\n".join(figures) + "\n      <!-- GALLERY:END -->"
    new_page, n = re.subn(
        r"<!-- GALLERY:START -->.*?<!-- GALLERY:END -->", block, page, flags=re.S
    )
    if n != 1:
        print("ERROR: gallery markers not found in index.html", file=sys.stderr)
        return 1
    if new_page != page:
        open(INDEX, "w").write(new_page)

    with open(DATA, "w") as fh:
        json.dump({"photos": ordered}, fh, indent=2)
        fh.write("\n")
    print(f"Gallery built: {len(figures)} photos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
