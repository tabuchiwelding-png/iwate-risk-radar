#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fetch_listed.py - 全国の上場企業をEDINETから取得して data/listed.json を生成"""

import io
import csv
import json
import os
import zipfile
import hashlib
import urllib.request
import datetime

EDINET_URLS = [
    "https://disclosure2dl.edinet-fsa.go.jp/searchdocument/codelist/Edinetcode.zip",
]

PREF = {
    "北海道": (43.064, 141.347), "青森県": (40.824, 140.740), "岩手県": (39.704, 141.153),
    "宮城県": (38.269, 140.872), "秋田県": (39.719, 140.102), "山形県": (38.240, 140.364),
    "福島県": (37.750, 140.468), "茨城県": (36.342, 140.447), "栃木県": (36.566, 139.884),
    "群馬県": (36.391, 139.060), "埼玉県": (35.857, 139.649), "千葉県": (35.605, 140.123),
    "東京都": (35.689, 139.692), "神奈川県": (35.448, 139.643), "新潟県": (37.902, 139.023),
    "富山県": (36.695, 137.211), "石川県": (36.595, 136.626), "福井県": (36.065, 136.222),
    "山梨県": (35.664, 138.568), "長野県": (36.651, 138.181), "岐阜県": (35.391, 136.722),
    "静岡県": (34.977, 138.383), "愛知県": (35.180, 136.907), "三重県": (34.730, 136.509),
    "滋賀県": (35.005, 135.869), "京都府": (35.021, 135.756), "大阪府": (34.686, 135.520),
    "兵庫県": (34.691, 135.183), "奈良県": (34.685, 135.833), "和歌山県": (34.226, 135.168),
    "鳥取県": (35.504, 134.238), "島根県": (35.472, 133.051), "岡山県": (34.662, 133.935),
    "広島県": (34.397, 132.460), "山口県": (34.186, 131.471), "徳島県": (34.066, 134.559),
    "香川県": (34.340, 134.043), "愛媛県": (33.842, 132.766), "高知県": (33.560, 133.531),
    "福岡県": (33.607, 130.418), "佐賀県": (33.249, 130.300), "長崎県": (32.745, 129.874),
    "熊本県": (32.790, 130.742), "大分県": (33.238, 131.613), "宮崎県": (31.911, 131.424),
    "鹿児島県": (31.560, 130.558), "沖縄県": (26.212, 127.681),
}

CITY = {
    "千代田区": ("東京都", 35.694, 139.753), "中央区": ("東京都", 35.671, 139.772),
    "港区": ("東京都", 35.658, 139.751), "新宿区": ("東京都", 35.694, 139.703),
    "文京区": ("東京都", 35.708, 139.752), "渋谷区": ("東京都", 35.664, 139.698),
    "品川区": ("東京都", 35.609, 139.730), "目黒区": ("東京都", 35.641, 139.698),
    "大田区": ("東京都", 35.561, 139.716), "世田谷区": ("東京都", 35.646, 139.653),
    "豊島区": ("東京都", 35.726, 139.717), "江東区": ("東京都", 35.673, 139.817),
    "台東区": ("東京都", 35.713, 139.780), "墨田区": ("東京都", 35.710, 139.801),
    "中野区": ("東京都", 35.707, 139.664), "杉並区": ("東京都", 35.700, 139.636),
    "北区": ("東京都", 35.753, 139.734), "板橋区": ("東京都", 35.751, 139.709),
    "練馬区": ("東京都", 35.736, 139.652), "足立区": ("東京都", 35.775, 139.804),
    "葛飾区": ("東京都", 35.743, 139.847), "江戸川区": ("東京都", 35.707, 139.868),
    "荒川区": ("東京都", 35.736, 139.783),
    "横浜市": ("神奈川県", 35.444, 139.638), "川崎市": ("神奈川県", 35.531, 139.703),
    "さいたま市": ("埼玉県", 35.861, 139.646), "千葉市": ("千葉県", 35.607, 140.106),
    "名古屋市": ("愛知県", 35.182, 136.906), "大阪市": ("大阪府", 34.694, 135.502),
    "京都市": ("京都府", 35.012, 135.768), "神戸市": ("兵庫県", 34.690, 135.196),
    "福岡市": ("福岡県", 33.590, 130.402), "札幌市": ("北海道", 43.062, 141.354),
    "仙台市": ("宮城県", 38.268, 140.870), "広島市": ("広島県", 34.385, 132.456),
    "北九州市": ("福岡県", 33.883, 130.875), "堺市": ("大阪府", 34.573, 135.483),
    "浜松市": ("静岡県", 34.711, 137.726), "静岡市": ("静岡県", 34.976, 138.383),
    "新潟市": ("新潟県", 37.916, 139.036), "岡山市": ("岡山県", 34.655, 133.919),
    "熊本市": ("熊本県", 32.803, 130.708), "金沢市": ("石川県", 36.561, 136.656),
    "徳島市": ("徳島県", 34.070, 134.555), "高松市": ("香川県", 34.340, 134.043),
    "松山市": ("愛媛県", 33.839, 132.766), "高知市": ("高知県", 33.560, 133.531),
    "鳴門市": ("徳島県", 34.173, 134.609),
}

DEFAULT = ("不明", 35.68, 139.69)


def jitter(name, lat, lng):
    h = hashlib.md5(name.encode("utf-8")).hexdigest()
    dlat = (int(h[0:4], 16) / 65535.0 - 0.5) * 0.16
    dlng = (int(h[4:8], 16) / 65535.0 - 0.5) * 0.22
    return round(lat + dlat, 5), round(lng + dlng, 5)


def geocode(addr, has_seccode):
    a = (addr or "").replace(" ", "").replace("　", "")
    best = None
    best_pos = len(a) + 1
    for p in PREF:
        pos = a.find(p)
        if pos != -1 and pos < best_pos:
            best, best_pos = p, pos
    if best:
        return best, PREF[best][0], PREF[best][1]
    for c in CITY:
        if c in a:
            pr, lat, lng = CITY[c]
            return pr, lat, lng
    if has_seccode:
        return DEFAULT[0], DEFAULT[1], DEFAULT[2]
    return None, None, None


def download_codelist():
    last = None
    for url in EDINET_URLS:
        try:
            print("[fetch] trying", url[:60])
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            print("[fetch]", len(data), "bytes downloaded")
            return data
        except Exception as e:
            print("[fetch] failed:", e)
            last = e
    raise RuntimeError("All EDINET URLs failed: " + str(last))


def parse_codelist(zb):
    zf = zipfile.ZipFile(io.BytesIO(zb))
    name = next((n for n in zf.namelist() if n.lower().endswith(".csv")), None)
    if not name:
        raise RuntimeError("CSV not found")
    text = zf.read(name).decode("cp932", errors="replace")
    lines = text.splitlines()
    hi = 0
    for i, ln in enumerate(lines[:5]):
        if "ＥＤＩＮＥＴ" in ln or "EDINET" in ln:
            hi = i
            break
    return list(csv.DictReader(lines[hi:]))


def col(row, *cands):
    for c in cands:
        for k in row.keys():
            if k and c in k:
                return (row[k] or "").strip()
    return ""


def main():
    out = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "listed.json"))
    try:
        rows = parse_codelist(download_codelist())
    except Exception as e:
        print("[error]", e)
        return

    companies = []
    skipped = 0
    pc = {}
    for row in rows:
        listed = col(row, "上場区分")
        if "上場" not in listed or "非上場" in listed:
            continue
        name = col(row, "提出者名")
        if not name or "提出者名" in name:
            continue
        addr = col(row, "所在地")
        sec = col(row, "証券コード")
        pref, lat, lng = geocode(addr, bool(sec))
        if not pref:
            skipped += 1
            continue
        lat, lng = jitter(name, lat, lng)
        pc[pref] = pc.get(pref, 0) + 1
        companies.append({
            "name": name, "prefecture": pref, "address": addr,
            "lat": lat, "lng": lng,
            "industry": col(row, "提出者業種") or "—",
            "sec_code": sec, "corp": col(row, "提出者法人番号"),
        })

    companies.sort(key=lambda c: (c["prefecture"], c["name"]))
    data = {
        "schema_version": 1,
        "last_updated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": "金融庁 EDINET コード一覧",
        "count": len(companies),
        "pref_counts": pc,
        "companies": companies,
    }
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("[done]", len(companies), "listed companies written")
    print("[done] skipped:", skipped)
    print("[done] top:", sorted(pc.items(), key=lambda x: -x[1])[:10])


if __name__ == "__main__":
    main()
