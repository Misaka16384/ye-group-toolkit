#!/usr/bin/env python3
"""Zero-dependency CLI to query the dynamically synced YE Group Toolkit knowledge base.

Fetch order:
  1. GitHub Raw (instant, zero CDN lag)
  2. jsDelivr CDN (campus/mainland China friendly mirror)
  3. Local repo kb/ snapshot (if running inside a cloned repo)
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

REPO = "Misaka16384/ye-group-toolkit"
BRANCH = "main"
PUBLIC_PORTAL = "https://yurucamp.notion.site/ye-group-toolkit"

RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"
CDN_BASE = f"https://cdn.jsdelivr.net/gh/{REPO}@{BRANCH}"

SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_KB_CANDIDATES = [
    SCRIPT_DIR.parents[2] / "kb",  # repo root/kb
    SCRIPT_DIR.parent / "kb",      # skill dir/kb (if bundled)
]


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def fetch_bytes(rel_path: str, timeout: float = 30.0, local_only: bool = False) -> tuple[bytes, str]:
    """Return (raw_bytes, source_label)."""
    rel_path = rel_path.lstrip("/")
    quoted = urllib.parse.quote(rel_path, safe="/")
    errors: list[str] = []

    if not local_only:
        for label, base in (("github-raw", RAW_BASE), ("jsdelivr-cdn", CDN_BASE)):
            url = f"{base}/{quoted}"
            req = urllib.request.Request(url, headers={"User-Agent": "ye-group-toolkit-skill/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    return resp.read(), label
            except Exception as exc:
                errors.append(f"{label}: {exc}")

    sub = rel_path[3:] if rel_path.startswith("kb/") else rel_path
    for kb_dir in LOCAL_KB_CANDIDATES:
        candidate = kb_dir / sub
        if candidate.is_file():
            return candidate.read_bytes(), f"local:{candidate}"

    detail = "; ".join(errors) if errors else "no local kb/ found"
    raise RuntimeError(
        f"无法拉取 {rel_path}（{detail}）。可直接访问公开网页：{PUBLIC_PORTAL}"
    )


def fetch_text(rel_path: str, timeout: float = 12.0, local_only: bool = False) -> tuple[str, str]:
    """Return (content, source_label)."""
    raw, label = fetch_bytes(rel_path, timeout=timeout, local_only=local_only)
    return raw.decode("utf-8"), label


def fetch_manifest(local_only: bool = False) -> tuple[dict[str, Any], str]:
    text, src = fetch_text("kb/manifest.json", local_only=local_only)
    return json.loads(text), src


def cmd_list(args: argparse.Namespace) -> int:
    text, src = fetch_text("kb/index.md", local_only=args.local)
    print(f"<!-- source: {src} -->")
    print(text)
    return 0


def resolve_page(manifest: dict[str, Any], target: str) -> dict[str, Any] | None:
    pages = manifest.get("pages", [])
    for p in pages:
        if target == p["slug"] or target == p["id"] or target == p["id"].replace("-", ""):
            return p
    lowered = target.lower()
    for p in pages:
        if lowered in p["slug"].lower() or lowered in p["title"].lower():
            return p
    return None


def cmd_read(args: argparse.Namespace) -> int:
    target = args.target.strip()
    manifest, _ = fetch_manifest(local_only=args.local)
    matched = resolve_page(manifest, target)

    if matched is None:
        print(f"未找到页面：{target}\n可用 slug 列表：", file=sys.stderr)
        for p in manifest.get("pages", []):
            print(f"  - {p['slug']}  ({p['title']})", file=sys.stderr)
        return 1

    text, src = fetch_text(matched["path"], local_only=args.local)
    print(f"<!-- source: {src} | notion: {matched['public_url']} -->")
    print(text)
    return 0


def cmd_download(args: argparse.Namespace) -> int:
    target = args.target.strip()
    manifest, _ = fetch_manifest(local_only=args.local)
    matched = resolve_page(manifest, target)
    if matched is None:
        print(f"未找到页面：{target}", file=sys.stderr)
        return 1

    assets = matched.get("assets", [])
    if not assets:
        print(
            f"页面「{matched['title']}」没有可直下的镜像附件（可访问原页查看：{matched['public_url']}）。"
        )
        return 0

    want = args.filename.strip().lower() if args.filename else ""
    selected = [a for a in assets if not want or want in a["name"].lower()]
    if not selected:
        print(f"未找到匹配「{args.filename}」的附件。本页可用附件：", file=sys.stderr)
        for a in assets:
            print(f"  - {a['name']}", file=sys.stderr)
        return 1

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    for a in selected:
        data, src = fetch_bytes(a["path"], local_only=args.local)
        dest = out_dir / a["name"]
        dest.write_bytes(data)
        print(f"已下载：{dest} ({len(data)} bytes, source={src})")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    keyword = args.keyword.strip().lower()
    manifest, src = fetch_manifest(local_only=args.local)
    pages = manifest.get("pages", [])

    hits: list[tuple[dict[str, Any], str]] = []
    for p in pages:
        meta_blob = " ".join(
            [
                p.get("title", ""),
                p.get("category", ""),
                p.get("summary", ""),
                " ".join(p.get("tags", [])),
                p.get("slug", ""),
            ]
        ).lower()
        if keyword in meta_blob:
            hits.append((p, "metadata"))
            continue
        if args.full:
            try:
                body, _ = fetch_text(p["path"], local_only=args.local)
                if keyword in body.lower():
                    hits.append((p, "content"))
            except Exception:
                pass

    print(f"<!-- source: {src} | synced_at: {manifest.get('synced_at', 'unknown')} -->")
    if not hits:
        print(f"未找到包含「{args.keyword}」的条目。可尝试 `list` 查看全部目录或加 `--full` 全文检索。")
        return 0

    print(f"找到 {len(hits)} 条匹配结果：\n")
    for p, where in hits:
        cat = f" [{p['category']}]" if p.get("category") else ""
        print(f"- **{p['title']}**{cat} (`slug: {p['slug']}`, 命中: {where})")
        if p.get("summary"):
            print(f"  - 简介：{p['summary']}")
        if p.get("assets"):
            names = ", ".join(a["name"] for a in p["assets"])
            print(f"  - 可直下附件：{names}（`python query.py download {p['slug']}`）")
        print(f"  - 网页直达：{p['public_url']}")
        print(f"  - 读取命令：`python query.py read {p['slug']}`")
    return 0


def main() -> int:
    _configure_stdio()
    parser = argparse.ArgumentParser(
        description="查询 YE Group Toolkit 动态知识库（无需浏览器、无需 Notion Token）"
    )
    parser.add_argument("--local", action="store_true", help="仅读取本地 kb/ 快照（离线模式）")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="显示全站目录索引")
    p_list.set_defaults(func=cmd_list)

    p_read = sub.add_parser("read", help="读取指定页面完整 Markdown")
    p_read.add_argument("target", help="页面 slug、标题关键词或页面 ID")
    p_read.set_defaults(func=cmd_read)

    p_search = sub.add_parser("search", help="按关键词搜索条目")
    p_search.add_argument("keyword", help="搜索关键词")
    p_search.add_argument("--full", action="store_true", help="同时检索所有页面正文")
    p_search.set_defaults(func=cmd_search)

    p_dl = sub.add_parser("download", help="下载指定页面的模板/文件附件（如 .zip/.tex/.pdf）")
    p_dl.add_argument("target", help="页面 slug、标题关键词或页面 ID")
    p_dl.add_argument("filename", nargs="?", default="", help="可选：只下载匹配该名称的文件")
    p_dl.add_argument("--out", default=".", help="保存目录（默认当前目录）")
    p_dl.set_defaults(func=cmd_download)

    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
