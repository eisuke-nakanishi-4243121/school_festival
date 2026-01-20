# 学園祭店舗管理システム

学園祭の出店情報を管理し、来場者向けにインタラクティブなWebマップを提供するPythonアプリケーションです。

## 概要

このシステムは、学園祭の運営を効率化するための2つのインターフェースを提供します。

- **運営者向け管理画面（Tkinter）**: 店舗の登録・編集・削除を行うデスクトップアプリ
- **来場者向けマップ（Folium）**: 登録された店舗をインタラクティブな地図上に表示するWebページ

**対象エリア**: 盛岡市大通3丁目1-19周辺（岩手県盛岡市）

## 主な機能

### v2.0の新機能
- **インタラクティブな地図選択**: Leaflet.jsベースの高度な座標選択機能
- **ブラウザ統合**: クリップボード経由でシームレスに座標を転送
- **簡潔なUI**: 手動入力と地図選択に特化したシンプルな画面設計
- **視覚的デザイン強化**: アイコン付きボタン、改善されたレイアウト

### コア機能
- 店舗情報の登録（名前、座標、説明、商品リスト）
- 複数商品の動的追加・削除
- 地図上での座標選択（クリック選択）
- リアルタイム座標表示
- 座標のクリップボードコピー
- 度分秒（DMS）形式の座標対応
- 店舗の一覧表示と削除
- 来場者向けHTMLマップ自動生成

## システム要件

- **Python**: 3.8以上
- **OS**: Windows、macOS、Linux
- **必須ライブラリ**:
  - `folium` (地図生成)
  - `tkinter` (標準ライブラリ - GUI)
  - `sqlite3` (標準ライブラリ - データベース)

## セットアップ

### 1. 仮想環境の作成

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化（Windows）
venv\Scripts\activate

# 仮想環境の有効化（macOS/Linux）
source venv/bin/activate
```

### 2. 依存関係のインストール

```bash
pip install folium
```

### 3. データベース初期化

初回起動時に自動的にSQLiteデータベース（`festival_stores.db`）が作成されます。手動での設定は不要です。

## 使用方法

### 運営者画面（店舗管理）

```bash
python main.py admin
```

または引数なしで実行（デフォルト動作）：

```bash
python main.py
```

#### 店舗登録の流れ

1. **座標の選択**
   - **地図から選択**: 🗺️ボタンをクリックして、ブラウザで開く地図上をクリック
   - **手動入力**: 緯度・経度を直接入力（小数点形式またはDMS形式）

2. **店舗情報の入力**
   - 店舗名
   - 店舗説明

3. **商品の登録**
   - 商品名と価格を入力
   - 「商品を追加」ボタンで複数商品を登録
   - 削除ボタンで不要な商品を削除

4. **プレビューと登録**
   - 👁️「プレビュー」で地図上の位置を確認
   - 🏪「登録」ボタンで店舗をデータベースに保存

### 来場者向けマップ生成

```bash
python main.py visitor
```

このコマンドは以下を実行します：
- データベースから全店舗情報を取得
- Foliumを使用してインタラクティブなHTMLマップを生成
- `festival_visitor_map.html` として保存
- デフォルトのWebブラウザでマップを自動表示

### ヘルプの表示

```bash
python main.py help
```

## ファイル構成

```
school_festival/
│
├── main.py                     # アプリケーションのエントリーポイント
├── admin_app.py                # 運営者向けTkinter GUI
├── visitor_map.py              # 来場者向けFoliumマップ生成
├── map_selector.py             # インタラクティブ地図座標選択機能
├── database.py                 # SQLiteデータベース操作
├── store_manager.py            # ビジネスロジック層
├── locations.py                # 位置情報定義（旧プリセットシステム）
│
├── festival_stores.db          # SQLiteデータベース（自動生成）
├── festival_visitor_map.html   # 生成されるWebマップ
│
├── venv/                       # Python仮想環境
├── .gitignore                  # Gitの除外設定
├── CLAUDE.md                   # 開発ガイド（Claude Code用）
└── README.md                   # このファイル
```

## データベース構造

### `stores` テーブル
```sql
CREATE TABLE stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    description TEXT
);
```

### `products` テーブル
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    store_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    price INTEGER NOT NULL,
    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE
);
```

## 技術仕様

### 座標システム
- **座標系**: WGS84 十進法度数（Decimal Degrees）
- **地図中心**: (39.7033, 141.1436)
- **デフォルトズームレベル**: 17

### 座標フォーマット
システムは以下の形式をサポート：
- 十進法: `(39.7034, 141.1434)`
- 度分秒（DMS）: `39°42'12.8"N 141°08'38.6"E`

### 依存ライブラリ
- **folium**: 地図生成とマーカー配置
- **tkinter**: デスクトップGUI（Python標準ライブラリ）
- **sqlite3**: データベース管理（Python標準ライブラリ）
- **Leaflet.js**: ブラウザベースのインタラクティブ地図（CDN経由）

## 開発とテスト

### データベース状態確認

```bash
# 店舗数の確認
python -c "import sqlite3; conn = sqlite3.connect('festival_stores.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM stores'); print(f'Current stores: {cursor.fetchone()[0]}'); conn.close()"
```

### データベースの手動初期化

```bash
python database.py
```

### テストマップ生成

```bash
python visitor_map.py
```

## トラブルシューティング

### foliumが見つからないエラー

```bash
pip install folium
```

### データベース接続エラー

1. `festival_stores.db` が存在することを確認
2. ファイルの権限を確認
3. 必要に応じて `database.py` を直接実行して再初期化

### 地図選択が動作しない

1. ブラウザのポップアップブロックを無効化
2. クリップボードへのアクセス権限を確認
3. 一時的なHTMLファイルが生成されているか確認

## バージョン履歴

### v2.0 (2025-01-13)
- インタラクティブな地図選択システムの実装
- ブラウザ統合によるシームレスな座標転送
- プリセット位置ドロップダウンの削除
- UIの視覚的強化（アイコン、レイアウト改善）
- `map_selector.py` の新規追加

### v1.2
- プリセット位置ドロップダウンの追加
- 動的商品リストUI
- リアルタイム座標表示
- クリックでコピー機能
- DMS座標形式対応

### v1.0
- 初期リリース
- 基本的な店舗管理機能
- Foliumマップ生成

## ライセンス

このプロジェクトは教育目的で作成されています。

## 開発者向け情報

詳細な開発ガイドは [CLAUDE.md](CLAUDE.md) を参照してください。

## サポート

問題が発生した場合は、以下を確認してください：
1. 仮想環境が有効化されているか
2. 必要なライブラリがインストールされているか
3. Pythonのバージョンが3.8以上か

---

**開発環境**: Python 3.8+ | Folium 0.20.0 | SQLite3
