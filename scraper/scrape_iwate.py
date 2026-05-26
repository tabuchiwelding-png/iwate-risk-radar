#!/usr/bin/env python3
"""
岩手リスクレーダー - 倒産情報自動取得スクリプト

JC-NET (n-seikei.jp) の東北倒産情報ページから
岩手県内の新規倒産情報を抽出し、JSON で出力する。

GitHub Actions から毎日 6:00 JST に自動実行される想定。

Usage:
    python scrape_iwate.py [--dry-run]
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ============= 設定 =============
TARGET_URL = "https://n-seikei.jp/webpages/touhoku.html"
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "bankruptcies.json"
USER_AGENT = "IwateRiskRadar/1.0 (private research; contact: your-email@example.com)"
JST = timezone(timedelta(hours=9))
REQUEST_TIMEOUT = 30
SLEEP_BETWEEN = 2  # 礼儀正しいスクレイピング


def fetch_html(url: str) -> str:
    """対象URLからHTMLを取得"""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "ja,en;q=0.7",
    }
    resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding
    return resp.text


def parse_entries(html: str) -> list[dict]:
    """JC-NETのHTMLから【岩手...】で始まるエントリを抽出"""
    soup = BeautifulSoup(html, "html.parser")
    entries = []
    text_content = soup.get_text("\n")

    pattern = re.compile(
        r"【岩手([^】]+)】"
        r"\s*([^／\n]+?)"
        r"／\s*([^\s\d]+)"
        r"[^\n]*?"
        r"(\d{4})年(\d{1,2})月(\d{1,2})日"
    )

    for m in pattern.finditer(text_content):
        city = m.group(1).strip()
        name = m.group(2).strip()
        status = m.group(3).strip()
        year, month, day = int(m.group(4)), int(m.group(5)), int(m.group(6))

        name = re.sub(r"\s+", " ", name).strip()
        name_normalized = name.replace("(株)", "(株)").replace("（株）", "(株)")

        form_match = re.search(r"^(\(株\)|\(有\)|\(合\)|\(同\)|株式会社|有限会社|合同会社)\s*(.+)$", name_normalized)
        if form_match:
            form = form_match.group(1)
            short_name = form_match.group(2)
        else:
            form_match = re.search(r"^(.+?)(\(株\)|\(有\)|\(合\)|\(同\))$", name_normalized)
            if form_match:
                short_name = form_match.group(1)
                form = form_match.group(2)
            else:
                form = ""
                short_name = name_normalized

        try:
            date = datetime(year, month, day).strftime("%Y-%m-%d")
        except ValueError:
            continue

        entries.append({
            "name": short_name,
            "form": form,
            "city": city,
            "status": status,
            "date": date,
            "year": year,
            "month": month,
            "day": day,
            "source": "JC-NET",
            "source_url": TARGET_URL,
            "scraped_at": datetime.now(JST).isoformat(),
        })

    seen = set()
    unique = []
    for e in entries:
        key = (e["name"], e["date"])
        if key not in seen:
            seen.add(key)
            unique.append(e)

    return unique


def load_existing() -> dict:
    if not OUTPUT_FILE.exists():
        return {
            "schema_version": 1,
            "last_updated": "",
            "last_scrape_status": "",
            "companies": [],
        }
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data: dict):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def merge_entries(existing: dict, new_entries: list) -> tuple:
    existing_keys = {(c["name"], c.get("date", "")) for c in existing.get("companies", [])}
    added = []

    for entry in new_entries:
        key = (entry["name"], entry["date"])
        if key not in existing_keys:
            existing.setdefault("companies", []).append(entry)
            added.append(entry)
            existing_keys.add(key)

    existing["companies"].sort(key=lambda c: c.get("date", ""), reverse=True)
    existing["last_updated"] = datetime.now(JST).isoformat()

    return existing, added


def notify_added(added: list):
    if not added:
        print("✓ 新規倒産情報なし")
        return
    print(f"✓ 新規倒産情報を {len(added)} 件追加:")
    for c in added:
        print(f"  - {c['date']} {c['form']}{c['name']} ({c['city']}) / {c['status']}")


def main():
    parser = argparse.ArgumentParser(description="岩手県倒産情報スクレイパー")
    parser.add_argument("--dry-run", action="store_true", help="ファイル保存せず結果表示のみ")
    args = parser.parse_args()

    print(f"[{datetime.now(JST).isoformat()}] スクレイピング開始")
    print(f"  Target: {TARGET_URL}")

    try:
        html = fetch_html(TARGET_URL)
        time.sleep(SLEEP_BETWEEN)
    except requests.RequestException as e:
        print(f"✗ HTTP取得失敗: {e}", file=sys.stderr)
        existing = load_existing()
        existing["last_scrape_status"] = f"failed: {e}"
        existing["last_attempted"] = datetime.now(JST).isoformat()
        if not args.dry_run:
            save(existing)
        sys.exit(1)

    print(f"  HTML取得成功: {len(html):,} 文字")

    new_entries = parse_entries(html)
    print(f"  パース結果: 岩手県内エントリ {len(new_entries)} 件")

    existing = load_existing()
    merged, added = merge_entries(existing, new_entries)
    merged["last_scrape_status"] = f"ok: parsed {len(new_entries)}, added {len(added)}"

    notify_added(added)

    if args.dry_run:
        print("(dry-run: 保存スキップ)")
    else:
        save(merged)
        print(f"✓ {OUTPUT_FILE} に保存完了 (合計 {len(merged['companies'])} 社)")


if __name__ == "__main__":
    main()
