#!/usr/bin/env python3
"""Inventory the public UT BIO 406D Central Texas plant image archive."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


ARCHIVE_URL = "https://web.biosci.utexas.edu/bio406d/PlantPics_archive.htm"


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[dict[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            values = dict(attrs)
            self._href = values.get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href is not None:
            self.links.append({"href": self._href, "text": clean_text(" ".join(self._text))})
            self._href = None
            self._text = []


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self._title_parts: list[str] = []
        self._body_parts: list[str] = []
        self._row: list[dict[str, object]] | None = None
        self._cell: dict[str, object] | None = None
        self.rows: list[list[dict[str, object]]] = []
        self.all_images: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "tr":
            self._row = []
        elif tag in {"td", "th"} and self._row is not None:
            self._cell = {"images": [], "text": []}
        elif tag == "img":
            src = values.get("src")
            if src:
                image = {
                    "src": src,
                    "alt": values.get("alt") or "",
                    "width": values.get("width") or "",
                    "height": values.get("height") or "",
                }
                self.all_images.append(image)
                if self._cell is not None:
                    images = self._cell["images"]
                    assert isinstance(images, list)
                    images.append(image)

    def handle_data(self, data: str) -> None:
        self._body_parts.append(data)
        if self._in_title:
            self._title_parts.append(data)
        if self._cell is not None:
            text = self._cell["text"]
            assert isinstance(text, list)
            text.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
            self.title = clean_text(" ".join(self._title_parts))
        elif tag in {"td", "th"} and self._cell is not None and self._row is not None:
            text = self._cell["text"]
            assert isinstance(text, list)
            self._cell["text"] = clean_text(" ".join(text))
            self._row.append(self._cell)
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None

    @property
    def body_text(self) -> str:
        return clean_text(" ".join(self._body_parts))


def fetch(url: str, attempts: int = 3) -> bytes:
    headers = {"User-Agent": "Hays-Botany-private-study-audit/1.0"}
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=45) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(0.4 * (attempt + 1))
    raise RuntimeError(f"Could not fetch {url}: {last_error}")


def decode(payload: bytes) -> str:
    for encoding in ("utf-8", "windows-1252", "latin-1"):
        try:
            return payload.decode(encoding)
        except UnicodeDecodeError:
            continue
    return payload.decode("latin-1", errors="replace")


def family_from_text(text: str) -> str:
    candidates = re.findall(r"\b[A-Z][A-Z-]{1,}(?:ACEAE|DAE)\b", text[:900])
    return candidates[0].title() if candidates else "Unknown"


def page_record(link: dict[str, str]) -> dict[str, object]:
    url = urllib.parse.urljoin(ARCHIVE_URL, link["href"])
    url = url.replace(
        "http://www.sbs.utexas.edu/mbierner/bio406d/",
        "https://web.biosci.utexas.edu/bio406d/",
    )
    html = decode(fetch(url))
    parser = PageParser()
    parser.feed(html)

    images: list[dict[str, object]] = []
    for row_index, row in enumerate(parser.rows):
        next_row = parser.rows[row_index + 1] if row_index + 1 < len(parser.rows) else []
        for cell_index, cell in enumerate(row):
            cell_images = cell.get("images") or []
            if not cell_images:
                continue
            own_caption = clean_text(str(cell.get("text") or ""))
            next_caption = ""
            if cell_index < len(next_row):
                candidate = next_row[cell_index]
                if not candidate.get("images"):
                    next_caption = clean_text(str(candidate.get("text") or ""))
            caption = own_caption or next_caption
            for image in cell_images:
                image_url = urllib.parse.urljoin(url, str(image["src"]))
                images.append(
                    {
                        **image,
                        "url": image_url,
                        "caption": caption,
                    }
                )

    recorded_urls = {str(image["url"]) for image in images}
    for image in parser.all_images:
        image_url = urllib.parse.urljoin(url, image["src"])
        if image_url in recorded_urls:
            continue
        images.append(
            {
                **image,
                "url": image_url,
                "caption": clean_text(image.get("alt") or ""),
            }
        )
        recorded_urls.add(image_url)

    return {
        "index_label": link["text"],
        "url": url,
        "title": parser.title or link["text"],
        "family": family_from_text(parser.body_text),
        "body_text": parser.body_text,
        "images": images,
        "image_count": len(images),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()

    index_html = decode(fetch(ARCHIVE_URL))
    link_parser = LinkParser()
    link_parser.feed(index_html)
    page_links: list[dict[str, str]] = []
    seen: set[str] = set()
    for link in link_parser.links:
        absolute = urllib.parse.urljoin(ARCHIVE_URL, link["href"])
        path = urllib.parse.urlparse(absolute).path.lower()
        if "/images/pics/" not in path or not path.endswith((".htm", ".html")):
            continue
        if absolute in seen:
            continue
        seen.add(absolute)
        page_links.append(link)

    records: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(page_record, link): link for link in page_links}
        for completed, future in enumerate(concurrent.futures.as_completed(futures), 1):
            link = futures[future]
            try:
                records.append(future.result())
            except Exception as error:  # audit output must retain every failure
                errors.append({"link": link["href"], "label": link["text"], "error": str(error)})
            if completed % 40 == 0:
                print(f"reviewed {completed}/{len(page_links)} pages", flush=True)

    records.sort(key=lambda item: (str(item["family"]), str(item["title"])))
    family_counts: dict[str, dict[str, int]] = {}
    for record in records:
        family = str(record["family"])
        bucket = family_counts.setdefault(family, {"pages": 0, "images": 0})
        bucket["pages"] += 1
        bucket["images"] += int(record["image_count"])

    output = {
        "archive_url": ARCHIVE_URL,
        "archive_statement": re.search(r"currently have links for\s+\d+\s+species", index_html, re.I).group(0)
        if re.search(r"currently have links for\s+\d+\s+species", index_html, re.I)
        else "",
        "index_links": len(page_links),
        "pages_fetched": len(records),
        "images_indexed": sum(int(record["image_count"]) for record in records),
        "errors": errors,
        "family_counts": family_counts,
        "pages": records,
    }
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({key: output[key] for key in ["archive_statement", "index_links", "pages_fetched", "images_indexed"]}, indent=2))
    print(f"errors: {len(errors)}")
    for family in ["Asteraceae", "Poaceae", "Fabaceae", "Euphorbiaceae", "Lamiaceae", "Cyperaceae"]:
        print(f"{family}: {family_counts.get(family, {'pages': 0, 'images': 0})}")


if __name__ == "__main__":
    main()
