#!/usr/bin/env python3
"""Prism Thief site quality gate (stdlib only).

Checks, against the files on disk:
  - every internal link/image/script/style referenced by the HTML pages exists
  - index.html and prints.html carry title, description, canonical, og:image
  - the photo-data JSON-LD block is present in index.html
  - every image file is within the per-file weight budget
  - sitemap.xml and feed.xml are well-formed XML
  - gallery.json is valid and in sync with photos/ and images/

Usage: python tools/check_site.py [site_root]   (default: repo root)
Exit code 0 = pass, 1 = failures printed to stdout.
"""
import json
import os
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
PAGES = ["index.html", "prints.html", "404.html"]
META_PAGES = ["index.html", "prints.html"]
IMAGE_BUDGET = 500_000  # bytes per image file
failures = []


def fail(msg):
    failures.append(msg)


class RefCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ("href", "src", "srcset") and value:
                self.refs.append(value)


def check_refs():
    for page in PAGES:
        path = os.path.join(ROOT, page)
        if not os.path.exists(path):
            fail(f"{page}: page missing")
            continue
        parser = RefCollector()
        parser.feed(open(path, encoding="utf-8").read())
        for ref in parser.refs:
            if ref.startswith(("http://", "https://", "mailto:", "#", "data:")):
                continue
            target = ref.split("#")[0].split("?")[0]
            if not target:
                continue
            local = target.lstrip("/")
            if local == "" or local.endswith("/"):
                local += "index.html"
            if not os.path.exists(os.path.join(ROOT, local)):
                fail(f"{page}: broken reference -> {ref}")


def check_meta():
    for page in META_PAGES:
        text = open(os.path.join(ROOT, page), encoding="utf-8").read()
        for needle, label in [
            ("<title>", "title"),
            ('name="description"', "meta description"),
            ('rel="canonical"', "canonical"),
            ('property="og:image"', "og:image"),
        ]:
            if needle not in text:
                fail(f"{page}: missing {label}")
    index = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    if "PHOTODATA:START" not in index:
        fail("index.html: photo-data JSON-LD block missing")


def check_images():
    images = os.path.join(ROOT, "images")
    total = 0
    for f in sorted(os.listdir(images)):
        size = os.path.getsize(os.path.join(images, f))
        total += size
        if size > IMAGE_BUDGET:
            fail(f"images/{f}: {size // 1024} KB over the {IMAGE_BUDGET // 1000} KB budget")
    print(f"images/: {len(os.listdir(images))} files, {total // 1024} KB total")


def check_xml():
    for name in ("sitemap.xml", "feed.xml"):
        try:
            ET.parse(os.path.join(ROOT, name))
        except Exception as e:
            fail(f"{name}: not well-formed XML ({e})")


def check_gallery_sync():
    try:
        data = json.load(open(os.path.join(ROOT, "gallery.json")))
    except Exception as e:
        fail(f"gallery.json: invalid ({e})")
        return
    slugs = [p["slug"] for p in data.get("photos", [])]
    for slug in slugs:
        for ext in ("jpg", "webp"):
            if not os.path.exists(os.path.join(ROOT, "images", f"{slug}.{ext}")):
                fail(f"gallery: images/{slug}.{ext} missing")
    photos = {
        os.path.splitext(f)[0].lower().replace(" ", "-")
        for f in os.listdir(os.path.join(ROOT, "photos"))
        if f.lower().endswith((".jpg", ".jpeg"))
    }
    import re

    def slugify(name):
        return re.sub(r"[^a-z0-9]+", "-", os.path.splitext(name)[0].lower()).strip("-")

    photo_slugs = {
        slugify(f)
        for f in os.listdir(os.path.join(ROOT, "photos"))
        if f.lower().endswith((".jpg", ".jpeg"))
    }
    for s in photo_slugs - set(slugs):
        fail(f"gallery: photos/ has {s} but gallery.json does not (run the pipeline)")
    for s in set(slugs) - photo_slugs:
        fail(f"gallery: gallery.json lists {s} but photos/ does not have it")


def main():
    check_refs()
    check_meta()
    check_images()
    check_xml()
    check_gallery_sync()
    if failures:
        print("SITE CHECK FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("SITE CHECK PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
