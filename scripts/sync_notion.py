#!/usr/bin/env python3
"""Sync YE Group Toolkit from Notion (official read-only REST API) into Markdown under kb/.

Zero third-party dependencies (Python 3.10+ standard library only).

Environment variables:
  NOTION_TOKEN       Required. Notion Internal Integration Secret (read-only).
  NOTION_ROOT_PAGE   Optional. Root page ID (default: c95c62ebd494411b9628ba081cbe1a9c).
  PUBLIC_SITE_ORIGIN Optional. Public Notion site origin (default: https://yurucamp.notion.site).
  PUBLIC_ROOT_URL    Optional. Public root URL (default: https://yurucamp.notion.site/ye-group-toolkit).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

DEFAULT_ROOT_PAGE = "c95c62ebd494411b9628ba081cbe1a9c"
DEFAULT_PUBLIC_ORIGIN = "https://yurucamp.notion.site"
DEFAULT_PUBLIC_ROOT_URL = "https://yurucamp.notion.site/ye-group-toolkit"

REPO_ROOT = Path(__file__).resolve().parents[1]
KB_DIR = REPO_ROOT / "kb"
PAGES_DIR = KB_DIR / "pages"
ASSETS_DIR = KB_DIR / "assets"
MAX_ASSET_BYTES = int(os.environ.get("MAX_ASSET_MB", "25")) * 1024 * 1024


def sanitize_filename(name: str, fallback: str = "attachment.bin") -> str:
    base = Path(name.split("?")[0]).name.strip()
    base = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", base)
    return base or fallback


def download_binary(url: str, max_bytes: int = MAX_ASSET_BYTES) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": "ye-group-toolkit-sync/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            cl = resp.headers.get("Content-Length")
            if cl and int(cl) > max_bytes:
                return None
            chunks: list[bytes] = []
            total = 0
            while True:
                buf = resp.read(65536)
                if not buf:
                    break
                total += len(buf)
                if total > max_bytes:
                    return None
                chunks.append(buf)
            return b"".join(chunks)
    except Exception:
        return None


def normalize_id(raw: str) -> str:
    return raw.replace("-", "").strip().lower()


def public_page_url(page_id: str, origin: str, root_id: str, root_url: str) -> str:
    clean = normalize_id(page_id)
    if clean == normalize_id(root_id):
        return root_url
    return f"{origin.rstrip('/')}/{clean}"


def make_slug(title: str, page_id: str, used: set[str]) -> str:
    # Prefer ASCII/Chinese-friendly readable slug + short ID suffix for stability
    clean_id = normalize_id(page_id)[:8]
    ascii_part = re.sub(r"[^a-zA-Z0-9]+", "-", title).strip("-").lower()
    if ascii_part and len(ascii_part) >= 3:
        base = f"{ascii_part[:36]}-{clean_id}"
    else:
        base = f"page-{clean_id}"
    slug = base
    n = 2
    while slug in used:
        slug = f"{base}-{n}"
        n += 1
    used.add(slug)
    return slug


class NotionClient:
    def __init__(self, token: str) -> None:
        self.token = token

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{NOTION_API_BASE}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
            "User-Agent": "ye-group-toolkit-sync/1.0",
        }
        for attempt in range(4):
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as err:
                if err.code in (429, 500, 502, 503, 504) and attempt < 3:
                    retry_after = float(err.headers.get("Retry-After", 1.5 * (attempt + 1)))
                    time.sleep(retry_after)
                    continue
                payload = err.read().decode("utf-8", "ignore")
                raise RuntimeError(f"Notion API {method} {path} failed ({err.code}): {payload}") from err
            except urllib.error.URLError:
                if attempt < 3:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise
        raise RuntimeError(f"Notion API {method} {path} exhausted retries")

    def get_page(self, page_id: str) -> dict[str, Any]:
        return self._request("GET", f"/pages/{page_id}")

    def get_database(self, database_id: str) -> dict[str, Any]:
        return self._request("GET", f"/databases/{database_id}")

    def query_database(self, database_id: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            payload: dict[str, Any] = {"page_size": 100}
            if cursor:
                payload["start_cursor"] = cursor
            res = self._request("POST", f"/databases/{database_id}/query", payload)
            rows.extend(res.get("results", []))
            if not res.get("has_more"):
                break
            cursor = res.get("next_cursor")
        return rows

    def list_block_children(self, block_id: str) -> list[dict[str, Any]]:
        blocks: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            q = f"/blocks/{block_id}/children?page_size=100"
            if cursor:
                q += f"&start_cursor={cursor}"
            res = self._request("GET", q)
            blocks.extend(res.get("results", []))
            if not res.get("has_more"):
                break
            cursor = res.get("next_cursor")
        return blocks


def rich_text_to_md(items: list[dict[str, Any]], origin: str, root_id: str, root_url: str) -> str:
    parts: list[str] = []
    for item in items or []:
        t = item.get("type")
        plain = item.get("plain_text", "")
        if t == "equation":
            expr = item.get("equation", {}).get("expression", plain)
            parts.append(f"${expr}$")
            continue
        if t == "mention":
            m = item.get("mention", {})
            if m.get("type") == "page":
                pid = m.get("page", {}).get("id", "")
                if pid:
                    parts.append(f"[{plain}]({public_page_url(pid, origin, root_id, root_url)})")
                    continue
            if m.get("type") == "link_preview":
                u = m.get("link_preview", {}).get("url", "")
                if u:
                    parts.append(f"[{plain or u}]({u})")
                    continue
        text = plain
        href = item.get("href")
        ann = item.get("annotations", {})
        if ann.get("code"):
            text = f"`{text}`"
        else:
            if ann.get("bold"):
                text = f"**{text}**"
            if ann.get("italic"):
                text = f"*{text}*"
            if ann.get("strikethrough"):
                text = f"~~{text}~~"
        if href:
            text = f"[{text}]({href})"
        parts.append(text)
    return "".join(parts)


def extract_page_properties(page: dict[str, Any]) -> dict[str, Any]:
    props = page.get("properties", {})
    title = ""
    category = ""
    summary = ""
    tags: list[str] = []

    for name, val in props.items():
        ptype = val.get("type")
        if ptype == "title":
            title = "".join(x.get("plain_text", "") for x in val.get("title", [])).strip()
        elif ptype == "select" and name in ("分类", "Category"):
            sel = val.get("select")
            if sel:
                category = sel.get("name", "")
        elif ptype == "rich_text" and name in ("简介", "Summary"):
            summary = "".join(x.get("plain_text", "") for x in val.get("rich_text", [])).strip()
        elif ptype == "multi_select" and name in ("标签", "Tags"):
            tags = [opt.get("name", "") for opt in val.get("multi_select", []) if opt.get("name")]

    icon_obj = page.get("icon") or {}
    icon = icon_obj.get("emoji", "") if icon_obj.get("type") == "emoji" else ""

    return {
        "title": title or "Untitled",
        "icon": icon,
        "category": category,
        "summary": summary,
        "tags": tags,
        "last_edited_time": page.get("last_edited_time", ""),
    }


def render_blocks(
    client: NotionClient,
    block_id: str,
    origin: str,
    root_id: str,
    root_url: str,
    discovered_child_pages: list[dict[str, str]],
    discovered_databases: list[dict[str, str]],
    page_slug: str,
    page_assets: list[dict[str, Any]],
    indent: int = 0,
) -> str:
    blocks = client.list_block_children(block_id)
    lines: list[str] = []
    prefix = "  " * indent
    numbered_counter = 0

    for blk in blocks:
        btype = blk.get("type", "")
        data = blk.get(btype, {}) or {}
        has_children = bool(blk.get("has_children"))

        if btype != "numbered_list_item":
            numbered_counter = 0

        if btype in ("heading_1", "heading_2", "heading_3"):
            lvl = int(btype[-1])
            txt = rich_text_to_md(data.get("rich_text", []), origin, root_id, root_url).strip()
            lines.append(f"\n{'#' * lvl} {txt}\n")
            if has_children:
                child_md = render_blocks(
                    client, blk["id"], origin, root_id, root_url, discovered_child_pages, discovered_databases, page_slug, page_assets, indent
                )
                if child_md.strip():
                    lines.append(child_md)
        elif btype == "paragraph":
            txt = rich_text_to_md(data.get("rich_text", []), origin, root_id, root_url)
            if txt.strip():
                lines.append(f"{prefix}{txt}\n")
            if has_children:
                child_md = render_blocks(
                    client, blk["id"], origin, root_id, root_url, discovered_child_pages, discovered_databases, page_slug, page_assets, indent + 1
                )
                if child_md.strip():
                    lines.append(child_md)
        elif btype == "bulleted_list_item":
            txt = rich_text_to_md(data.get("rich_text", []), origin, root_id, root_url)
            lines.append(f"{prefix}- {txt}")
            if has_children:
                child_md = render_blocks(
                    client, blk["id"], origin, root_id, root_url, discovered_child_pages, discovered_databases, page_slug, page_assets, indent + 1
                )
                if child_md.strip():
                    lines.append(child_md)
        elif btype == "numbered_list_item":
            numbered_counter += 1
            txt = rich_text_to_md(data.get("rich_text", []), origin, root_id, root_url)
            lines.append(f"{prefix}{numbered_counter}. {txt}")
            if has_children:
                child_md = render_blocks(
                    client, blk["id"], origin, root_id, root_url, discovered_child_pages, discovered_databases, page_slug, page_assets, indent + 1
                )
                if child_md.strip():
                    lines.append(child_md)
        elif btype == "to_do":
            mark = "x" if data.get("checked") else " "
            txt = rich_text_to_md(data.get("rich_text", []), origin, root_id, root_url)
            lines.append(f"{prefix}- [{mark}] {txt}")
        elif btype == "quote":
            txt = rich_text_to_md(data.get("rich_text", []), origin, root_id, root_url)
            lines.append(f"\n> {txt}\n")
        elif btype == "callout":
            icon_obj = data.get("icon") or {}
            icon = icon_obj.get("emoji", "") if icon_obj.get("type") == "emoji" else ""
            txt = rich_text_to_md(data.get("rich_text", []), origin, root_id, root_url)
            head = f"{icon} {txt}".strip()
            quote_lines = [f"> {ln}" if ln.strip() else ">" for ln in head.splitlines()]
            if has_children:
                child_md = render_blocks(
                    client, blk["id"], origin, root_id, root_url, discovered_child_pages, discovered_databases, page_slug, page_assets, 0
                )
                for ln in child_md.strip().splitlines():
                    quote_lines.append(f"> {ln}" if ln.strip() else ">")
            lines.append("\n" + "\n".join(quote_lines) + "\n")
        elif btype == "toggle":
            txt = rich_text_to_md(data.get("rich_text", []), origin, root_id, root_url)
            lines.append(f"\n<details>\n<summary>{txt}</summary>\n")
            if has_children:
                child_md = render_blocks(
                    client, blk["id"], origin, root_id, root_url, discovered_child_pages, discovered_databases, page_slug, page_assets, 0
                )
                lines.append(child_md.strip())
            lines.append("\n</details>\n")
        elif btype == "code":
            lang = data.get("language", "text")
            if lang == "plain text":
                lang = "text"
            code = "".join(x.get("plain_text", "") for x in data.get("rich_text", []))
            fence = "````" if "```" in code else "```"
            lines.append(f"\n{fence}{lang}\n{code}\n{fence}\n")
        elif btype == "equation":
            expr = data.get("expression", "")
            lines.append(f"\n$$\n{expr}\n$$\n")
        elif btype == "divider":
            lines.append("\n---\n")
        elif btype == "table":
            rows = client.list_block_children(blk["id"])
            md_rows: list[str] = []
            for idx, r in enumerate(rows):
                cells = (r.get("table_row") or {}).get("cells", [])
                rendered = [
                    rich_text_to_md(c, origin, root_id, root_url).replace("\n", "<br>").replace("|", "\\|")
                    for c in cells
                ]
                md_rows.append("| " + " | ".join(rendered) + " |")
                if idx == 0:
                    md_rows.append("| " + " | ".join(["---"] * len(rendered)) + " |")
            if md_rows:
                lines.append("\n" + "\n".join(md_rows) + "\n")
        elif btype in ("column_list", "column", "synced_block"):
            if has_children:
                child_md = render_blocks(
                    client, blk["id"], origin, root_id, root_url, discovered_child_pages, discovered_databases, page_slug, page_assets, indent
                )
                if child_md.strip():
                    lines.append(child_md)
        elif btype == "bookmark":
            url = data.get("url", "")
            cap = rich_text_to_md(data.get("caption", []), origin, root_id, root_url).strip() or url
            if url:
                lines.append(f"\n- 🔗 [{cap}]({url})\n")
        elif btype == "embed":
            url = data.get("url", "")
            if url:
                lines.append(f"\n- 🌐 嵌入网页：[{url}]({url})\n")
        elif btype in ("file", "pdf"):
            file_type = data.get("type", "")
            src_url = (data.get(file_type) or {}).get("url", "") if file_type in ("file", "external") else ""
            raw_name = (
                data.get("name")
                or rich_text_to_md(data.get("caption", []), origin, root_id, root_url).strip()
                or (urllib.parse.unquote(Path(src_url.split("?")[0]).name) if src_url else "")
                or f"attachment-{len(page_assets) + 1}.bin"
            )
            fname = sanitize_filename(raw_name, f"attachment-{len(page_assets) + 1}.bin")
            saved_rel = ""
            size_bytes = 0
            if src_url:
                blob = download_binary(src_url)
                if blob is not None:
                    dest_dir = ASSETS_DIR / page_slug
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    dest = dest_dir / fname
                    # Avoid collisions within same page
                    if dest.exists() and any(a["name"] == fname for a in page_assets):
                        stem, suffix = dest.stem, dest.suffix
                        fname = f"{stem}_{len(page_assets) + 1}{suffix}"
                        dest = dest_dir / fname
                    dest.write_bytes(blob)
                    saved_rel = f"kb/assets/{page_slug}/{fname}"
                    size_bytes = len(blob)
            if saved_rel:
                page_assets.append({"name": fname, "path": saved_rel, "size": size_bytes})
                size_kb = max(1, round(size_bytes / 1024))
                lines.append(
                    f"\n- 📎 **可直下附件**：`{fname}`（约 {size_kb} KB）— 可用命令 `python query.py download {page_slug} {fname}` 直接下载到本地\n"
                )
            else:
                lines.append(
                    f"\n- 📎 **附件**：`{fname}`（超出仓库镜像体积上限或外部链接，请前往本页对应的 Notion 网页链接下载）\n"
                )
        elif btype == "image":
            cap = rich_text_to_md(data.get("caption", []), origin, root_id, root_url).strip()
            note = f"：{cap}" if cap else ""
            lines.append(f"\n> 🖼️ *（原页包含示例截图{note}，请打开本页对应的 Notion 网页链接查看）*\n")
        elif btype == "child_page":
            ctitle = data.get("title", "子页面")
            cid = blk["id"]
            curl = public_page_url(cid, origin, root_id, root_url)
            discovered_child_pages.append({"id": cid, "title": ctitle})
            lines.append(f"\n- 📄 子页面：**[{ctitle}]({curl})**（详细正文已同步至对应知识库文件）\n")
        elif btype == "child_database":
            dtitle = data.get("title", "数据库")
            did = blk["id"]
            discovered_databases.append({"id": did, "title": dtitle})
            lines.append(f"\n*（内联数据库：**{dtitle}**，各条目详见目录索引 `kb/index.md` 与 `kb/pages/`）*\n")

    return "\n".join(lines)


def sync() -> None:
    token = os.environ.get("NOTION_TOKEN", "").strip()
    if not token:
        raise SystemExit("ERROR: NOTION_TOKEN environment variable is required.")

    root_id = os.environ.get("NOTION_ROOT_PAGE", DEFAULT_ROOT_PAGE).strip()
    origin = os.environ.get("PUBLIC_SITE_ORIGIN", DEFAULT_PUBLIC_ORIGIN).strip()
    root_url = os.environ.get("PUBLIC_ROOT_URL", DEFAULT_PUBLIC_ROOT_URL).strip()

    client = NotionClient(token)
    KB_DIR.mkdir(parents=True, exist_ok=True)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    # Clean stale exported pages and assets before writing fresh set
    for old_md in PAGES_DIR.glob("*.md"):
        old_md.unlink()
    if ASSETS_DIR.exists():
        shutil.rmtree(ASSETS_DIR)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    visited: set[str] = set()
    used_slugs: set[str] = set()
    manifest_pages: list[dict[str, Any]] = []

    def export_page(page_id: str, parent_title: str = "", preset_meta: dict[str, Any] | None = None) -> None:
        nid = normalize_id(page_id)
        if nid in visited:
            return
        visited.add(nid)

        page_obj = client.get_page(page_id)
        meta = extract_page_properties(page_obj)
        if preset_meta:
            for k in ("category", "summary", "tags"):
                if not meta.get(k) and preset_meta.get(k):
                    meta[k] = preset_meta[k]

        is_root = nid == normalize_id(root_id)
        slug = "home" if is_root else make_slug(meta["title"], page_id, used_slugs)
        pub_url = public_page_url(page_id, origin, root_id, root_url)

        child_pages: list[dict[str, str]] = []
        child_dbs: list[dict[str, str]] = []
        page_assets: list[dict[str, Any]] = []

        body_md = render_blocks(
            client, page_id, origin, root_id, root_url, child_pages, child_dbs, slug, page_assets
        ).strip()

        header_lines = [f"# {meta['icon']} {meta['title']}".strip(), ""]
        header_lines.append(f"- **网页直达（含附件/截图）**：{pub_url}")
        if meta["category"]:
            header_lines.append(f"- **分类**：{meta['category']}")
        if meta["tags"]:
            header_lines.append(f"- **标签**：{', '.join(meta['tags'])}")
        if parent_title:
            header_lines.append(f"- **所属页面**：{parent_title}")
        if page_assets:
            names = ", ".join(f"`{a['name']}`" for a in page_assets)
            header_lines.append(f"- **可直下附件**：{names}（`python query.py download {slug}`）")
        if meta["last_edited_time"]:
            header_lines.append(f"- **Notion 最后更新**：{meta['last_edited_time']}")
        header_lines.extend(["", "---", "", body_md, ""])

        rel_path = f"kb/pages/{slug}.md"
        (REPO_ROOT / rel_path).write_text("\n".join(header_lines), encoding="utf-8")

        manifest_pages.append(
            {
                "slug": slug,
                "id": page_id,
                "title": meta["title"],
                "icon": meta["icon"],
                "category": meta["category"],
                "summary": meta["summary"],
                "tags": meta["tags"],
                "parent": parent_title,
                "path": rel_path,
                "assets": page_assets,
                "public_url": pub_url,
                "last_edited_time": meta["last_edited_time"],
            }
        )

        # Recurse into child databases first (in clean order), then child pages
        for db in child_dbs:
            rows = client.query_database(db["id"])
            for row in rows:
                row_meta = extract_page_properties(row)
                export_page(row["id"], parent_title=meta["title"], preset_meta=row_meta)

        for cp in child_pages:
            export_page(cp["id"], parent_title=meta["title"])

    export_page(root_id)

    synced_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Sort non-root pages cleanly by category then title
    home_entries = [p for p in manifest_pages if p["slug"] == "home"]
    other_entries = sorted(
        [p for p in manifest_pages if p["slug"] != "home"],
        key=lambda x: (x["category"] or "zzzz", x["parent"], x["title"]),
    )
    ordered = home_entries + other_entries

    manifest = {
        "name": "YE Group Toolkit",
        "public_url": root_url,
        "synced_at": synced_at,
        "page_count": len(ordered),
        "pages": ordered,
    }
    (KB_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # Build human + AI friendly kb/index.md
    idx_lines = [
        "# 🍀 YE Group Toolkit 知识库索引",
        "",
        f"- **网页版主页**：{root_url}",
        f"- **同步时间（UTC）**：{synced_at}",
        f"- **收录页面数**：{len(ordered)}",
        "",
        "## 目录清单",
        "",
        "| 分类 | 标题 | `slug`（供 `query.py read` 使用） | 简介 | 可直下附件 | 网页直达 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for p in ordered:
        cat = p["category"] or ("主页" if p["slug"] == "home" else f"子页（{p['parent']}）")
        title_disp = f"{p['icon']} {p['title']}".strip().replace("|", "\\|")
        summary_disp = (p["summary"] or "").replace("|", "\\|")
        assets_disp = ", ".join(f"`{a['name']}`" for a in p.get("assets", [])) or "—"
        idx_lines.append(
            f"| {cat} | {title_disp} | `{p['slug']}` | {summary_disp} | {assets_disp} | [打开网页]({p['public_url']}) |"
        )
    idx_lines.append("")

    (KB_DIR / "index.md").write_text("\n".join(idx_lines), encoding="utf-8")
    print(f"Synced {len(ordered)} pages from Notion into {KB_DIR} at {synced_at}.")


if __name__ == "__main__":
    sync()
