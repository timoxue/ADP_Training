#!/usr/bin/env python3
"""
wiki_crawler.py — Crawl wiki/tutorial/docs sites and save as local Markdown.

Usage:
  python wiki_crawler.py <url> --outdir ./output
  python wiki_crawler.py <url> --outdir ./output --nav-selector "aside nav"
  python wiki_crawler.py <url> --outdir ./output --max-depth 3
  python wiki_crawler.py <url> --outdir ./output --resume
  python wiki_crawler.py <url> --outdir ./output --retry-failed
  python wiki_crawler.py --verify --outdir ./output
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import tempfile

import requests
from bs4 import BeautifulSoup
import markdownify as md_lib

# ── Constants ──────────────────────────────────────────────────────────────────

KNOWN_SELECTORS = [
    "nav.theme-doc-sidebar-menu",   # Docusaurus
    ".sidebar_node_modules",
    ".wy-menu-vertical",            # ReadTheDocs / Sphinx
    ".bd-sidenav",
    "#sidebar .ia-scrollable-section",  # Confluence
    "#mw-panel",                    # MediaWiki
    "aside nav",
    "nav[aria-label*='sidebar' i]",
    "[class*='sidebar'] nav",
    "[id*='sidebar'] nav",
]

CONTENT_SELECTORS = [
    "article", "main", ".markdown-body", ".doc-content",
    ".content-body", "[class*='content'] article",
    "#content", ".wiki-content", ".doc-content-bd",
]

REMOVE_SELECTORS = [
    "nav", "aside", "header", "footer",
    ".breadcrumb", ".pagination", ".edit-this-page",
    "#toc", ".feedback", "[class*='banner']",
]

RETRY_DELAYS = [1, 3, 8]

# ── NavNode ────────────────────────────────────────────────────────────────────

@dataclass
class NavNode:
    title: str
    url: str
    depth: int
    index: int
    children: list[NavNode] = field(default_factory=list)

# ── ContentExtractor ───────────────────────────────────────────────────────────

class ContentExtractor:
    def extract(self, html: str, base_url: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        content = self._select_content(soup)
        code_blocks = self._extract_code_blocks(content)
        self._remove_noise(content)
        markdown = md_lib.markdownify(str(content), heading_style="ATX", bullets="-")
        markdown = self._restore_code_blocks(markdown, code_blocks)
        return markdown.strip()

    def _select_content(self, soup):
        for selector in CONTENT_SELECTORS:
            el = soup.select_one(selector)
            if el:
                return el
        return soup.body or soup

    def _remove_noise(self, content):
        for selector in REMOVE_SELECTORS:
            for el in content.select(selector):
                el.decompose()

    def _extract_code_blocks(self, content) -> dict[str, tuple[str, str]]:
        """Replace <pre><code> elements with placeholders; return {placeholder: (lang, code)}."""
        blocks: dict[str, tuple[str, str]] = {}
        for i, pre in enumerate(content.find_all("pre")):
            code_el = pre.find("code")
            lang = ""
            classes_to_check = list(code_el.get("class") or []) + list(pre.get("class") or []) if code_el else list(pre.get("class") or [])
            for cls in classes_to_check:
                if cls.startswith("language-"):
                    lang = cls[9:]
                    break
            if code_el:
                text = code_el.get_text()
            else:
                text = pre.get_text()
            if not text.strip():
                pre.decompose()
                continue
            placeholder = f"WIKICODEBLOCK{uuid.uuid4().hex}ENDBLOCK"
            blocks[placeholder] = (lang, text)
            pre.replace_with(BeautifulSoup(f"<p>{placeholder}</p>", "html.parser").p)
        return blocks

    def _restore_code_blocks(self, md: str, blocks: dict) -> str:
        for placeholder, (lang, code) in blocks.items():
            fence = f"```{lang}\n{code.rstrip()}\n```"
            md = md.replace(placeholder, fence)
        return md

# ── NavParser ──────────────────────────────────────────────────────────────────

class NavParser:
    def __init__(self, page, manual_selector: str | None = None):
        self.page = page
        self.manual_selector = manual_selector

    def build_tree(self, url: str, max_depth: int | None = None) -> list[NavNode]:
        """Navigate to URL, detect sidebar, return NavNode tree. Requires self.page."""
        self.page.goto(url, wait_until="load", timeout=60000)
        if self.manual_selector:
            el = self.page.query_selector(self.manual_selector)
            if not el:
                raise ValueError(f"Selector not found: {self.manual_selector}")
            self._expand_collapsed(el)
            sidebar_html = el.inner_html()
        else:
            sidebar_html = self._find_sidebar()
            if sidebar_html is None:
                return []
        return self._parse_sidebar(sidebar_html, url, max_depth)

    def _find_sidebar(self) -> str | None:
        # Tier 1: known framework selectors
        for selector in KNOWN_SELECTORS:
            try:
                el = self.page.query_selector(selector)
                if el:
                    self._expand_collapsed(el)
                    return el.inner_html()
            except Exception:
                continue

        # Tier 2: heuristic — most links in left 30% of viewport
        best_el_handle = self.page.evaluate_handle("""() => {
            const threshold = window.innerWidth * 0.30;
            const candidates = [...document.querySelectorAll('nav, aside')];
            let best = null, bestLinks = -1;
            for (const el of candidates) {
                const rect = el.getBoundingClientRect();
                if (rect.right > threshold) continue;
                const links = el.querySelectorAll('a').length;
                if (links > bestLinks) { bestLinks = links; best = el; }
            }
            return best;
        }""")
        best_el = best_el_handle.as_element()
        sidebar_html = None
        if best_el:
            try:
                self._expand_collapsed(best_el)
                sidebar_html = best_el.inner_html()
            except Exception:
                sidebar_html = None
        if sidebar_html:
            return sidebar_html

        # Tier 3: manual fallback — screenshot + candidate list
        screenshot_path = os.path.join(os.getcwd(), "sidebar_debug.png")
        self.page.screenshot(path=screenshot_path)
        candidates = self.page.evaluate("""() => {
            return [...document.querySelectorAll('nav, aside')]
                .map((el, i) => ({
                    index: i,
                    tag: el.tagName.toLowerCase(),
                    id: el.id || '',
                    cls: (el.className || '').toString().split(' ')[0],
                    links: el.querySelectorAll('a').length,
                }))
                .sort((a, b) => b.links - a.links)
                .slice(0, 5);
        }""")
        print(f"\nCould not auto-detect sidebar. Screenshot: {screenshot_path}")
        print("Top candidates (by link count):")
        for c in candidates:
            tag = c["tag"]
            id_ = f"#{c['id']}" if c["id"] else ""
            cls_ = f".{c['cls']}" if c["cls"] else ""
            print(f"  {tag}{id_}{cls_}  ({c['links']} links)")
        print("Rerun with --nav-selector '<css-selector>'")
        return None

    def _expand_collapsed(self, el) -> None:
        """Click all collapsed nav items (multi-pass) so children render in the DOM."""
        # Try both aria-expanded and class-based expandable items (e.g. Tencent Cloud).
        EXPAND_SELECTORS = [
            "[aria-expanded='false']",
            ".tcd-menu__item--expandable",
        ]
        clicked_keys: set[str] = set()
        for _ in range(10):  # up to 10 rounds for nested collapsibles
            found_any = False
            for sel in EXPAND_SELECTORS:
                try:
                    items = el.query_selector_all(sel)
                except Exception:
                    continue
                for item in items:
                    try:
                        key = item.evaluate(
                            "el => el.tagName + '|' + el.className + '|' + el.textContent.slice(0,30)"
                        )
                        if key in clicked_keys:
                            continue
                        item.click()
                        clicked_keys.add(key)
                        self.page.wait_for_timeout(300)
                        found_any = True
                    except Exception:
                        pass
            if not found_any:
                break
        self.page.wait_for_timeout(500)  # final settle after all clicks

    def _parse_sidebar(self, html: str, base_url: str, max_depth: int | None) -> list[NavNode]:
        """Parse sidebar HTML into a NavNode tree.

        max_depth is the maximum depth index: 0 = root only, 1 = root + one child level.
        """
        base_domain = urlparse(base_url).netloc
        soup = BeautifulSoup(html, "html.parser")
        visited: set[str] = set()

        def parse_list(container, depth: int) -> list[NavNode]:
            if max_depth is not None and depth > max_depth:
                return []
            nodes = []
            items = [c for c in container.children if getattr(c, "name", None) == "li"]
            idx = 1
            for li in items:
                a = li.find("a", recursive=False)
                if not a:
                    # Section header with no own link — recurse children if any
                    sub = li.find(["ul", "ol"])
                    if sub:
                        nodes.extend(parse_list(sub, depth))  # keep same depth for header-only items
                    continue
                if not a.get("href"):
                    continue
                raw_href = a["href"].split("#")[0]
                if not raw_href:   # fragment-only href like "#section" → skip
                    continue
                href = urljoin(base_url, raw_href)
                href = href.rstrip("/") or href  # don't strip if href is just "/"
                if not href.startswith("http"):
                    continue
                if urlparse(href).netloc != base_domain:
                    continue
                if href in visited:
                    continue
                visited.add(href)
                title = a.get_text(strip=True) or href
                node = NavNode(title=title, url=href, depth=depth, index=idx)
                sub = li.find(["ul", "ol"])
                if sub:
                    node.children = parse_list(sub, depth + 1)
                nodes.append(node)
                idx += 1
            return nodes

        root_list = soup.find(["ul", "ol"])
        if root_list:
            return parse_list(root_list, 0)

        # Flat fallback: all links in sidebar
        nodes = []
        for idx, a in enumerate(soup.find_all("a", href=True), 1):
            raw_href = a["href"].split("#")[0]
            if not raw_href:
                continue
            href = urljoin(base_url, raw_href)
            href = href.rstrip("/") or href  # don't strip if href is just "/"
            if not href.startswith("http") or urlparse(href).netloc != base_domain:
                continue
            if href in visited:
                continue
            visited.add(href)
            nodes.append(NavNode(title=a.get_text(strip=True), url=href, depth=0, index=idx))
        return nodes

# ── ImageDownloader ────────────────────────────────────────────────────────────

class ImageDownloader:
    def __init__(self, outdir: str):
        self.outdir = outdir
        self._seen: dict[str, str] = {}  # sha256 → relative path from outdir

    def download(self, img_url: str) -> str | None:
        """Download image. Returns path relative to outdir, or None on skip/failure."""
        if img_url.startswith("data:"):
            return None
        if img_url.startswith("//"):
            img_url = "https:" + img_url
        parsed = urlparse(img_url)
        if parsed.path.lower().endswith(".svg"):
            return None

        domain = re.sub(r"[^\w.-]", "_", parsed.netloc) or "unknown"
        filename = os.path.basename(parsed.path) or "image"

        data: bytes | None = None
        for attempt in range(3):
            try:
                resp = requests.get(img_url, timeout=30,
                                    headers={"User-Agent": "wiki-crawler/1.0"})
                resp.raise_for_status()
                data = resp.content
                break
            except Exception:
                if attempt < 2:
                    time.sleep(RETRY_DELAYS[attempt])

        if data is None:
            return None

        digest = hashlib.sha256(data).hexdigest()
        if digest in self._seen:
            return self._seen[digest]

        safe_name = f"{digest[:8]}_{re.sub(r'[^\w.-]', '_', filename)}"
        img_dir = os.path.join(self.outdir, "assets", "images", domain)
        os.makedirs(img_dir, exist_ok=True)
        img_path = os.path.join(img_dir, safe_name)
        with open(img_path, "wb") as f:
            f.write(data)

        rel = os.path.relpath(img_path, self.outdir).replace("\\", "/")
        self._seen[digest] = rel
        return rel

    def process_markdown(self, md: str, page_file: str) -> str:
        """Rewrite all ![alt](http-url) in md to locally downloaded relative paths."""
        page_dir = os.path.dirname(page_file)

        def replace_img(m: re.Match) -> str:
            alt, raw_url = m.group(1), m.group(2)
            url = raw_url.split()[0]  # strip optional Markdown title
            # Skip SVG and data URIs without marking as failure
            parsed_url = urlparse(url)
            if url.startswith("data:") or parsed_url.path.lower().endswith(".svg"):
                return m.group(0)
            if not (url.startswith("http") or url.startswith("//")):
                return m.group(0)
            local = self.download(url)
            if local is None:
                return m.group(0) + "<!-- image download failed -->"
            abs_local = os.path.join(self.outdir, local)
            rel = os.path.relpath(abs_local, page_dir).replace("\\", "/")
            return f"![{alt}]({rel})"

        return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_img, md)

# ── FileWriter ──────────────────────────────────────────────────────────────────

class FileWriter:
    def __init__(self, outdir: str):
        self.outdir = outdir
        os.makedirs(outdir, exist_ok=True)

    def slugify(self, text: str) -> str:
        text = re.sub(r"[^\w\s-]", "", text.lower())
        slug = re.sub(r"[\s_]+", "-", text).strip("-")
        return slug or "page"

    def dir_for(self, node: NavNode, parent_dir: str) -> str:
        """Return the section directory path for a node (used when node has children)."""
        nn = str(node.index).zfill(2)
        return os.path.join(parent_dir, f"{nn}-{self.slugify(node.title)}")

    def write_page(self, node: NavNode, parent_dir: str, content_md: str) -> str:
        """Write Markdown with YAML frontmatter. Returns absolute file path."""
        nn = str(node.index).zfill(2)
        title_slug = self.slugify(node.title)
        raw_url_slug = urlparse(node.url).path.rstrip("/").split("/")[-1] or "index"
        url_slug = re.sub(r"[^\w-]", "-", raw_url_slug).strip("-") or "index"
        filename = f"{nn}-{title_slug}__{url_slug}.md"
        os.makedirs(parent_dir, exist_ok=True)
        filepath = os.path.join(parent_dir, filename)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        # Truncate at first control character to prevent YAML injection
        safe_title = re.split(r"[\r\n\t]", node.title)[0].strip()
        quoted_title = safe_title.replace('"', '\\"')
        frontmatter = (
            f"---\n"
            f'title: "{quoted_title}"\n'
            f"source_url: {node.url}\n"
            f"crawled_at: {now}\n"
            f"---\n\n"
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(frontmatter + content_md)
        return filepath

    def sha256_file(self, path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

# ── Manifest helpers ────────────────────────────────────────────────────────────

def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ── Post-processing ─────────────────────────────────────────────────────────────

def rewrite_internal_links(outdir: str, url_to_file: dict[str, str]):
    """Walk all .md files and rewrite [text](http://...) → [text](relative.md)."""
    for root, _dirs, files in os.walk(outdir):
        for fname in files:
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(root, fname)
            with open(fpath, encoding="utf-8") as f:
                content = f.read()

            def replace_link(m: re.Match) -> str:
                text, url = m.group(1), m.group(2)
                url_base = url.split("#")[0]
                anchor = url[len(url_base):]
                if url_base in url_to_file:
                    target_abs = os.path.join(outdir, url_to_file[url_base])
                    rel = os.path.relpath(target_abs, root).replace("\\", "/")
                    return f"[{text}]({rel}{anchor})"
                return m.group(0)

            new_content = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", replace_link, content)
            if new_content != content:
                dir_ = os.path.dirname(fpath)
                with tempfile.NamedTemporaryFile("w", encoding="utf-8",
                                                  dir=dir_, delete=False, suffix=".tmp") as tmp:
                    tmp.write(new_content)
                    tmp_path = tmp.name
                os.replace(tmp_path, fpath)


def generate_readme(outdir: str, site_url: str, site_title: str,
                    nodes: list[NavNode], url_to_file: dict[str, str]) -> str:
    """Generate top-level README.md with crawl stats and TOC tree."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    page_count = sum(1 for v in url_to_file.values() if v)
    lines = [
        f"# {site_title} — Crawled from {site_url}",
        f"> Crawled: {now}  Pages: {page_count}",
        "",
        "## Table of Contents",
    ]

    def toc_lines(nav_nodes: list[NavNode], indent: int = 0):
        for node in nav_nodes:
            prefix = "  " * indent + "- "
            if node.url in url_to_file:
                lines.append(f"{prefix}[{node.title}]({url_to_file[node.url]})")
            else:
                lines.append(f"{prefix}{node.title}")
            if node.children:
                toc_lines(node.children, indent + 1)

    toc_lines(nodes)
    readme_path = os.path.join(outdir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return readme_path


# ── Verify ──────────────────────────────────────────────────────────────────────

def verify(outdir: str) -> bool:
    manifest_path = os.path.join(outdir, "manifest.json")
    if not os.path.exists(manifest_path):
        print("No manifest.json found.")
        return False
    try:
        manifest = load_json(manifest_path)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Could not read manifest: {exc}")
        return False
    ok = corrupted = missing = 0
    for entry in manifest.get("pages", []):
        fpath = os.path.join(outdir, entry["file_path"])
        if not os.path.exists(fpath):
            print(f"  MISSING   {entry['file_path']}")
            missing += 1
        else:
            with open(fpath, "rb") as fh:
                actual = hashlib.sha256(fh.read()).hexdigest()
            if actual != entry["sha256"]:
                print(f"  CORRUPTED {entry['file_path']}")
                corrupted += 1
            else:
                ok += 1
    print(f"\nVerify: {ok} ok, {missing} missing, {corrupted} corrupted")
    return missing == 0 and corrupted == 0

# ── Core crawl ──────────────────────────────────────────────────────────────────

def crawl(
    start_url: str,
    outdir: str,
    nav_selector: str | None = None,
    max_depth: int | None = None,
    resume: bool = False,
    retry_failed: bool = False,
):
    from playwright.sync_api import sync_playwright

    manifest_path = os.path.join(outdir, "manifest.json")
    failed_path = os.path.join(outdir, "failed.json")

    # Build sets for resume / retry modes
    existing_ok: set[str] = set()
    existing_pages: list[dict] = []
    if resume and os.path.exists(manifest_path):
        m = load_json(manifest_path)
        existing_pages = m.get("pages", [])
        existing_ok = {p["url"] for p in existing_pages if p.get("status") == "ok"}

    retry_urls: set[str] | None = None
    if retry_failed and os.path.exists(failed_path):
        retry_urls = {f["url"] for f in load_json(failed_path)}

    writer = FileWriter(outdir)
    img_dl = ImageDownloader(outdir)
    extractor = ContentExtractor()

    pages_done: list[dict] = [p for p in existing_pages if p.get("status") == "ok"] if resume else []
    pages_failed: list[dict] = []
    url_to_file: dict[str, str] = {p["url"]: p["file_path"]
                                   for p in existing_pages if p.get("status") == "ok"}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        nav_parser = NavParser(page, manual_selector=nav_selector)
        print(f"Building nav tree from {start_url} ...")
        tree = nav_parser.build_tree(start_url, max_depth)
        if not tree:
            print("ERROR: Could not detect sidebar navigation. Use --nav-selector.")
            browser.close()
            return

        site_title = page.title() or urlparse(start_url).netloc
        print(f"Site: {site_title}  Nav nodes: {_count_nodes(tree)}")

        # Pre-seed with completed URLs so crawl_node skips them while still recursing their children
        visited: set[str] = set(existing_ok)

        def crawl_node(node: NavNode, parent_dir: str):
            if node.url in visited:
                # Still recurse children so they get their dirs
                if node.children:
                    child_dir = writer.dir_for(node, parent_dir)
                    for child in node.children:
                        crawl_node(child, child_dir)
                return
            visited.add(node.url)

            # Skip if retry_failed mode and not in failed list
            if retry_urls is not None and node.url not in retry_urls:
                if node.children:
                    child_dir = writer.dir_for(node, parent_dir)
                    for child in node.children:
                        crawl_node(child, child_dir)
                return

            # Crawl with retry
            for attempt in range(3):
                try:
                    page.goto(node.url, wait_until="load", timeout=30000)
                    html = page.content()
                    content_md = extractor.extract(html, node.url)
                    filepath = writer.write_page(node, parent_dir, content_md)
                    # Rewrite images in the written file
                    with open(filepath, encoding="utf-8") as fh:
                        raw = fh.read()
                    patched = img_dl.process_markdown(raw, filepath)
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(patched)
                    sha = writer.sha256_file(filepath)
                    rel = os.path.relpath(filepath, outdir).replace("\\", "/")
                    url_to_file[node.url] = rel
                    pages_done.append({
                        "url": node.url,
                        "file_path": rel,
                        "sha256": sha,
                        "images": [],
                        "status": "ok",
                    })
                    print(f"  OK  [{node.depth}] {node.title}")
                    break
                except Exception as e:
                    if attempt < 2:
                        print(f"  Retry {attempt + 1}/3: {node.title}: {e}")
                        time.sleep(RETRY_DELAYS[attempt])
                    else:
                        print(f"  FAIL {node.title}: {e}")
                        pages_failed.append({"url": node.url, "title": node.title,
                                             "error": str(e)})

            # Recurse into children regardless of success
            if node.children:
                child_dir = writer.dir_for(node, parent_dir)
                os.makedirs(child_dir, exist_ok=True)
                for child in node.children:
                    crawl_node(child, child_dir)

        for node in tree:
            crawl_node(node, outdir)

        browser.close()

    # Post-processing
    print("\nRewriting internal links ...")
    rewrite_internal_links(outdir, url_to_file)
    generate_readme(outdir, start_url, site_title, tree, url_to_file)

    # Write manifest + failed
    manifest = {
        "site": start_url,
        "crawled_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "pages": pages_done,
    }
    save_json(manifest_path, manifest)
    if pages_failed:
        save_json(failed_path, pages_failed)
        print(f"\n{len(pages_failed)} pages failed — see {failed_path}")

    print(f"\nDone. {len(pages_done)} pages saved to {outdir}")


def _count_nodes(nodes: list[NavNode]) -> int:
    return sum(1 + _count_nodes(n.children) for n in nodes)


# ── CLI ──────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="wiki-crawler — save docs/wiki sites as local Markdown files"
    )
    parser.add_argument("url", nargs="?", help="Starting URL to crawl")
    parser.add_argument("--outdir", default="./output", help="Output directory (default: ./output)")
    parser.add_argument("--nav-selector", default=None,
                        help="CSS selector override for sidebar nav")
    parser.add_argument("--max-depth", type=int, default=None,
                        help="Limit nav nesting depth")
    parser.add_argument("--resume", action="store_true",
                        help="Skip pages already in manifest with status: ok")
    parser.add_argument("--retry-failed", action="store_true",
                        help="Only re-run pages recorded in failed.json")
    parser.add_argument("--verify", action="store_true",
                        help="Integrity check only — no crawling")
    args = parser.parse_args()

    if args.verify:
        ok = verify(args.outdir)
        sys.exit(0 if ok else 1)

    if not args.url:
        parser.print_help()
        return

    crawl(
        start_url=args.url,
        outdir=args.outdir,
        nav_selector=args.nav_selector,
        max_depth=args.max_depth,
        resume=args.resume,
        retry_failed=args.retry_failed,
    )


if __name__ == "__main__":
    main()
