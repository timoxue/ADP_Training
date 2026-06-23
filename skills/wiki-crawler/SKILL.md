---
name: wiki-crawler
description: >
  Crawl any wiki, tutorial, or documentation website and save all pages as local
  Markdown files in a directory structure that mirrors the site's navigation sidebar.
  Use when the user provides a documentation/tutorial/wiki URL and wants to save it
  locally, or uses words like "crawl", "download", "mirror", "archive", "save offline",
  or "copy docs". Supports Docusaurus, ReadTheDocs, Sphinx, Confluence, MediaWiki,
  GitBook, Notion exports, and any site with a left-side navigation sidebar.
  Works on both public sites and login-required sites (uses the user's existing
  browser session via Playwright Chromium).
---

# Wiki Crawler Skill

## Quick Start

```bash
# Minimal — auto-detects sidebar
python scripts/wiki_crawler.py <url> --outdir ./output

# With manual sidebar selector (if auto-detection fails)
python scripts/wiki_crawler.py <url> --outdir ./output --nav-selector "aside nav"

# Limit depth
python scripts/wiki_crawler.py <url> --outdir ./output --max-depth 3

# Resume interrupted crawl (skips pages already in manifest)
python scripts/wiki_crawler.py <url> --outdir ./output --resume

# Re-run only failed pages
python scripts/wiki_crawler.py <url> --outdir ./output --retry-failed

# Integrity check only
python scripts/wiki_crawler.py --verify --outdir ./output
```

## Dependencies

```bash
pip install playwright markdownify beautifulsoup4 requests
playwright install chromium
```

## Output Structure

```
output/
├── README.md                           ← auto-generated TOC
├── assets/images/<domain>/             ← downloaded images
├── 01-getting-started/
│   ├── 01-installation__install.md
│   └── 02-quick-start__quickstart.md
├── 02-api-reference/
│   └── 01-authentication__auth.md
├── manifest.json                       ← URLs, file paths, SHA-256 checksums
└── failed.json                         ← pages that failed (if any)
```

Each `.md` file has YAML frontmatter:
```markdown
---
title: Installation
source_url: https://docs.example.com/docs/install
crawled_at: 2026-06-14T10:23:45
---
```

## Sidebar Detection

The script tries three tiers automatically:
1. **Known selectors** — Docusaurus, ReadTheDocs, Confluence, MediaWiki, etc.
2. **Heuristic** — largest `<nav>` or `<aside>` in the left 30% of the page
3. **Manual fallback** — saves `sidebar_debug.png` screenshot, prints candidate selectors, asks user to specify `--nav-selector`

## Login-Required Sites

Playwright Chromium launches a headed browser. Log in manually in the browser window that opens, then the crawl continues with your session.

## Notes

- Same image content (identical SHA-256) is downloaded only once; all references point to the same file.
- Internal links between crawled pages are rewritten to relative `.md` paths in a post-processing pass.
- Retry: 3 attempts per page with 1s → 3s backoff. Failures logged to `failed.json`.
- `--resume` skips pages with `status: ok` in `manifest.json` — safe to rerun after interruption.
- `--verify` exits 0 on success, exits 1 if any files are missing or corrupted.
