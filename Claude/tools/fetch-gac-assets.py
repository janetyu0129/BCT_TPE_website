#!/usr/bin/env python3
"""Self-host the Figma MCP assets that gac.html still links to.

gac.html was authored straight out of Figma and its <img> tags point at
https://www.figma.com/api/mcp/asset/<uuid> — temporary URLs that a public
visitor cannot load, so the page renders with broken images. Every other case
study page keeps its images under uploads/<page>/; this script does the same
for gac.

Usage (from anywhere):

    python3 Claude/tools/fetch-gac-assets.py            # download + rewrite
    python3 Claude/tools/fetch-gac-assets.py --dry-run  # just report

Re-running is safe: already-downloaded assets are skipped and URLs that have
already been rewritten are simply not found again.
"""

import argparse
import pathlib
import re
import sys
import urllib.error
import urllib.request

ASSET_RE = re.compile(r"https://www\.figma\.com/api/mcp/asset/([0-9a-fA-F-]+)")

# Magic bytes -> extension. Figma serves these without a reliable filename.
SIGNATURES = [
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpg"),
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
]


def guess_ext(data, content_type):
    for magic, ext in SIGNATURES:
        if data.startswith(magic):
            return ext
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    head = data[:400].lstrip()
    if head.startswith(b"<svg") or head.startswith(b"<?xml"):
        return "svg"
    if content_type:
        subtype = content_type.split("/")[-1].split(";")[0].strip()
        if subtype in {"png", "jpeg", "jpg", "gif", "webp", "svg+xml"}:
            return {"jpeg": "jpg", "svg+xml": "svg"}.get(subtype, subtype)
    return "bin"


def alt_slug(html, uuid):
    """Derive a readable name from the first non-empty alt= for this asset."""
    for match in re.finditer(r"<img[^>]*>", html):
        tag = match.group(0)
        if uuid not in tag:
            continue
        alt = re.search(r'alt="([^"]+)"', tag)
        if alt:
            slug = re.sub(r"[^a-z0-9]+", "-", alt.group(1).lower()).strip("-")
            if slug:
                return slug[:40]
    return None


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read(), resp.headers.get("Content-Type", "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("html", nargs="?", help="page to process (default: Claude/gac.html)")
    parser.add_argument("--dry-run", action="store_true", help="report without writing anything")
    args = parser.parse_args()

    claude_dir = pathlib.Path(__file__).resolve().parent.parent
    page = pathlib.Path(args.html).resolve() if args.html else claude_dir / "gac.html"
    if not page.is_file():
        sys.exit(f"not found: {page}")

    html = page.read_text(encoding="utf-8")
    uuids = sorted(set(ASSET_RE.findall(html)))
    if not uuids:
        print(f"{page.name}: no Figma asset URLs left — nothing to do.")
        return

    total_tags = len(ASSET_RE.findall(html))
    print(f"{page.name}: {total_tags} references, {len(uuids)} unique assets\n")
    if args.dry_run:
        for uuid in uuids:
            print(f"  {uuid}  {alt_slug(html, uuid) or ''}")
        return

    out_dir = page.parent / "uploads" / page.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    failed = []
    for i, uuid in enumerate(uuids, 1):
        url = f"https://www.figma.com/api/mcp/asset/{uuid}"
        short = uuid.split("-")[0]
        slug = alt_slug(html, uuid)
        stem = f"{slug}-{short}" if slug else short

        existing = list(out_dir.glob(f"{stem}.*"))
        if existing:
            name = existing[0].name
            print(f"  [{i:2}/{len(uuids)}] {name}  (already downloaded)")
        else:
            try:
                data, content_type = fetch(url)
            except (urllib.error.URLError, urllib.error.HTTPError, OSError) as err:
                reason = getattr(err, "code", None) or err
                print(f"  [{i:2}/{len(uuids)}] {short}  FAILED: {reason}")
                failed.append((uuid, reason))
                continue
            name = f"{stem}.{guess_ext(data, content_type)}"
            (out_dir / name).write_bytes(data)
            print(f"  [{i:2}/{len(uuids)}] {name}  ({len(data):,} bytes)")

        html = html.replace(url, f"uploads/{page.stem}/{name}")

    page.write_text(html, encoding="utf-8")

    remaining = len(ASSET_RE.findall(html))
    print(f"\nrewrote {page.name} -> uploads/{page.stem}/")
    if failed:
        print(f"{len(failed)} asset(s) could not be downloaded and still point at Figma:")
        for uuid, reason in failed:
            print(f"  {uuid}  ({reason})")
        print("\nThose URLs have expired. Re-export them from the source Figma file.")
    elif remaining == 0:
        print("all assets are now self-hosted.")


if __name__ == "__main__":
    main()
