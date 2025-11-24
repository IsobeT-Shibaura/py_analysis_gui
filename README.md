# Python GUI Tool (Windows Only)

Windows 向け最小構成の Python GUI ツール (Tkinter / wxPython)。クロスプラットフォーム対応コード・Docker 関連は削除済みです。

## 機能
- Tkinter: `app.py` シンプルカウンタ
- wxPython: `wx_app.py` 左固定メニュー + 複数ページ (Log / Results / Correction / Config プレースホルダ)
- ログファイル選択: Win32 ネイティブ (GetOpenFileNameW) → 失敗時 `wx.FileDialog` フォールバック
- ドラッグ&ドロップ: エクスプローラーからログファイルを直接テキストフィールドへ
- ダークテーマ: フラットなメニュー・アクセントカラー

## 実行方法
Tkinter:
```powershell
uv run app.py
```
wxPython:
```powershell
uv run wx_app.py
```

## 開発メモ
- 依存管理: `uv` + `pyproject.toml` (`uv add <name>` / `uv remove <name>` / `uv lock`)
- ネイティブファイルダイアログ: `ctypes` のみ利用 (追加依存なし)

### ログファイル選択詳細
1. Win32 API `GetOpenFileNameW` を呼び出しネイティブダイアログ表示
2. キャンセル/失敗時は `wx.FileDialog`
3. フィルタ: All Files / Log Files (*.log)
4. 複数選択・フォルダ選択は未対応 (将来拡張)

### ドラッグ&ドロップ (Windows)
1. `uv run wx_app.py` を起動
2. 「Register Log」ページのテキストフィールドへファイルをドロップ
3. パスが自動入力

## パッケージ管理 (uv / PowerShell)
```powershell
irm https://astral.sh/uv/install.ps1 | iex
uv sync
```

### よく使うコマンド
```powershell
uv sync          # 依存インストール
uv add wxPython  # 依存追加例
uv lock          # ロック再生成
uv pip list      # インストール確認
uv run wx_app.py # 実行
```

## トラブルシュート
- `ModuleNotFoundError: wx` → `uv sync` / `uv add wxPython==4.2.1`
- ネットワーク制限 → 事前にホイール取得し `uv pip install <wheel>`
- Python バージョン → 3.11 系推奨

## 開発反復フロー
1. コード編集 (`wx_app.py`)
2. `uv run wx_app.py`
3. 動作確認 → 再編集

ウォッチ (任意):
```powershell
uv add watchdog
watchmedo auto-restart -p '*.py' -R -- uv run wx_app.py
```

## 今後の拡張候補
- 設定ダイアログ / 永続化 (JSON / YAML)
- ログ解析・出力機能
- テーマ切替 (ライト/ダーク)

## Git 運用
機能単位でブランチを作成し PR で統合。

## ライセンス
必要に応じて後で追加予定。
