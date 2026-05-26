# 岩手リスクレーダー / Setup Guide

> 個人事業者・中小企業の経営者向け、岩手県内の倒産情報を自動取得するBI（Business Intelligence）ダッシュボード。
> Week 1 のゴール：**毎朝6時に自動で最新化される岩手版倒産マップ** を自分用に立ち上げる。

---

## 📦 含まれるファイル

```
iwate-risk-radar/
├── index.html                    ← BIマップ本体（ブラウザで開くだけで動く）
├── data/
│   ├── bankruptcies.json         ← 倒産情報（自動更新）
│   ├── steel.json                ← 鉄鋼関連企業（手動）
│   └── distressed.json           ← 業績懸念企業（手動）
├── scraper/
│   └── scrape_iwate.py           ← Python自動取得スクリプト
├── .github/workflows/
│   └── daily-scrape.yml          ← GitHub Actions（毎日6時実行）
├── requirements.txt              ← Python依存ライブラリ
└── SETUP.md                      ← この手順書
```

---

## 🚀 セットアップ手順（30分で完了）

### Step 1: GitHubアカウント作成（5分）

すでに持っている方はスキップ。

1. https://github.com にアクセス
2. 右上の「Sign up」をクリック
3. メールアドレス・パスワード・ユーザー名を入力
4. 無料プランで OK

### Step 2: 新しいリポジトリを作成（3分）

1. GitHubにログイン後、右上「+」→「New repository」
2. Repository name: `iwate-risk-radar`
3. Description: `岩手県倒産情報自動収集ダッシュボード`
4. **Public**（GitHub Pages無料公開用）または **Private**（自社専用、ただしGitHub Pagesは有料プラン必要）を選択
5. 「Add a README file」にチェック
6. 「Create repository」をクリック

### Step 3: ファイルをアップロード（10分）

**方法A: ブラウザから直接アップロード（簡単）**

1. リポジトリ画面で「Add file」→「Upload files」
2. このプロジェクトの全ファイル（フォルダごと）をドラッグ&ドロップ
3. 下部の「Commit changes」をクリック

> **注意:** GitHub の Web UI ではフォルダごとのアップロードが可能。`.github` フォルダ（隠しフォルダ）もアップロードする。

**方法B: Git コマンドラインから（推奨）**

```bash
git clone https://github.com/<あなたのユーザー名>/iwate-risk-radar.git
cd iwate-risk-radar
# このプロジェクトのファイルをここにコピー
git add .
git commit -m "Initial setup"
git push
```

### Step 4: GitHub Actions を有効化（2分）

1. リポジトリ画面の「Actions」タブをクリック
2. 「Daily Iwate Bankruptcy Scraper」というワークフローが表示される
3. 「I understand my workflows, go ahead and enable them」をクリック
4. **試しに手動実行：** 「Daily Iwate Bankruptcy Scraper」を選択 →「Run workflow」→「Run workflow」（緑ボタン）
5. 数秒〜1分で実行完了。緑のチェックマーク✅ が出れば成功

> **次回からは毎日 06:00 JST に自動実行されます。**

### Step 5: GitHub Pages で公開（5分・Public リポジトリの場合）

1. リポジトリの「Settings」タブ
2. 左メニュー「Pages」
3. Source: `Deploy from a branch`
4. Branch: `main`、Folder: `/ (root)`
5. 「Save」
6. 数分待つと、URLが表示される（例: `https://yourname.github.io/iwate-risk-radar/`）
7. スマホで開いて、Safariのシェアボタン→「ホーム画面に追加」でアプリ化

### Step 6: 動作確認（5分）

- ブラウザでURL（GitHub Pages のURL or `index.html` を直接ローカルで開く）にアクセス
- 「はじめる」をタップ
- マップが表示されればOK
- 上部に「MM.DD 更新 / WORST1」と最終更新日が表示される
- 1週間以内に追加された企業は 🆕 バッジ付き

---

## 🔁 自動更新の仕組み

```
[毎日 06:00 JST]
    ↓
GitHub Actions が起動
    ↓
Python: scraper/scrape_iwate.py 実行
    ↓
JC-NET (n-seikei.jp) から東北倒産情報を取得
    ↓
岩手県の新規倒産のみ抽出
    ↓
data/bankruptcies.json に追記
    ↓
自動で Git commit & push
    ↓
GitHub Pages 上のサイトに反映（数分以内）
    ↓
ブラウザを更新するだけで最新データが表示される
```

**運用コスト: ¥0/月**（GitHub 無料枠で完結）

---

## 🛠 ローカルで動かす場合

ブラウザでファイルを直接開くと、JSON fetch が CORS でブロックされる場合があります。
その場合はローカルサーバーを立てる：

```bash
cd iwate-risk-radar
python3 -m http.server 8000
# ブラウザで http://localhost:8000 を開く
```

---

## ✏️ データの手動編集

`data/steel.json`（鉄鋼関連企業）と `data/distressed.json`（業績懸念）は手動メンテナンス。
GitHubのWeb UIから直接編集可能：

1. ファイルをクリック
2. 鉛筆アイコン（Edit）
3. JSONを編集
4. 「Commit changes」

---

## 🔍 トラブルシューティング

### 「Actions」が動かない
- 「Settings」→「Actions」→「General」で `Allow all actions and reusable workflows` を選択
- リポジトリ作成直後は反映に数分かかる場合あり

### スクレイピングが失敗する
- JC-NETのサイト構造変更が原因の可能性
- `scrape_iwate.py` の `parse_entries` 関数を調整する必要あり
- Claude に「JC-NETのHTML構造が変わったので scrape_iwate.py のパターンを調整して」と相談

### GitHub Pages が 404 になる
- 公開まで5-10分かかる
- ブランチ設定が `main / root` になっているか確認
- `index.html` がルートにあるか確認

---

## ⚠️ 法的注意事項

### スクレイピングについて
- **個人利用（自社業務）の範囲では一般に許容される**
- 商用サービスとして他者に提供する場合は、JC-NET側に許諾を得るか、TSR/TDBの正規APIに切替を推奨
- スクレイパーは `User-Agent` を明示し、`time.sleep(2)` で礼儀正しいアクセスをしている

### 表示データについて
- 公開情報（破産公告・新聞報道）のみを集約しており、新規情報は生成していない
- 個人情報を含む内容は含まない（法人情報のみ）
- 万が一誤情報があれば、当該データを `bankruptcies.json` から手動削除可能

### 商用化（有料会員制）に向けて
- 特定商取引法表記（事業者名・住所・連絡先・返金規定）が必須
- 利用規約（免責事項・データ精度の限定保証）が必須
- これらは公開時までに弁護士と相談を推奨

---

## 🗓 次のステップ（Week 2-4）

### Week 2: EDINET連携（上場企業の決算自動取得）
- 金融庁EDINET APIから岩手県内7上場企業の有価証券報告書を毎日チェック
- 営業赤字・売上前年比-20%以上を自動フラグ
- `distressed.json` に自動追記

### Week 3: 与信カード機能（PWA化）
- Firebase 連携で取引先カードのCRUD
- iOSホーム画面追加でアプリっぽく使える
- メモ・チェック履歴を端末間で同期

### Week 4: テスト運用＋ブラッシュアップ
- 2-3人のテストユーザーで運用
- フィードバック反映
- 商標調査・サービス名決定

---

## 📞 詰まったら

Claude に「岩手リスクレーダーの〇〇でエラー」と相談。スクショ・エラーログを貼り付けで対応可能。

---

**Version:** 0.1.0 (MVP Week 1)
**Last Updated:** 2026-05-26
**License:** Private use only (currently)
