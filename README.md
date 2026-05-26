# 岩手リスクレーダー / Iwate Risk Radar

岩手県内の倒産情報を自動収集し、地図＋業界分析で可視化するビジネス・インテリジェンス・ダッシュボード。

![status](https://img.shields.io/badge/status-MVP-orange)
![auto-update](https://img.shields.io/badge/auto--update-daily%2006%3A00%20JST-success)
![cost](https://img.shields.io/badge/hosting-%C2%A50%2Fmonth-blue)

## 🎯 何ができる？

- 📍 **岩手県の倒産企業を実地図上で可視化**（Leaflet + OpenStreetMap）
- 🔄 **毎朝6時に自動更新**（GitHub Actions + Python スクレイパー）
- 📊 **4軸レーダーチャート** で東京・大阪・北海道・福岡と比較
- 🏭 **鉄鋼関連企業（生存）** と **業績懸念企業** のレイヤー切替
- 📋 **与信チェックリスト7項目** で取引前デューデリ
- 📱 スマホ縦持ち最優先、PC両対応

## 🚀 セットアップ

[SETUP.md](./SETUP.md) を参照。30分でデプロイ完了。

## 📦 構成

```
index.html              ← BIマップ本体
data/
  bankruptcies.json     ← 倒産情報（自動更新）
  steel.json            ← 鉄鋼関連企業
  distressed.json       ← 業績懸念企業
scraper/
  scrape_iwate.py       ← Python自動取得スクリプト
.github/workflows/
  daily-scrape.yml      ← GitHub Actions
```

## 🔍 データソース

- 公開情報のみ：TSR・TDB公開ニュース、JC-NET、岩手日報、官報
- 自動取得対象：JC-NET 東北倒産情報（個人利用）
- 手動メンテナンス：鉄鋼関連企業、業績懸念企業

## ⚠️ 注意

- 現状は個人利用・自社業務用
- 商用化（有料会員制公開）には特定商取引法表記・利用規約・データソース許諾の整備が必要
- データ精度は公開情報の範囲内（TSR/TDB有料情報には及ばない）

## 📅 ロードマップ

- [x] Week 1: 自動更新基盤（このリリース）
- [ ] Week 2: EDINET連携（上場企業決算自動）
- [ ] Week 3: 与信カード（Firebase / PWA化）
- [ ] Week 4: テスト運用
- [ ] Month 2-3: iOSネイティブ化検討（Capacitor or SwiftUI）
- [ ] Month 4+: 有料会員制ローンチ

---

**License:** Private (TBD)
**Maintainer:** （あなたの名前）
