# Python GUI Tool

Tkinter / wxPython を用いた最小構成の Python GUI ツールです。

## 機能 (初期状態)
 - Tkinter版: `app.py` シンプルカウンタ
 - wxPython版: `wx_app.py` サイドバー + 複数ページ (Log/Results/Correction/Config プレースホルダ) + ログファイル選択
 - Windows では可能なら OS 標準 IFileOpenDialog を利用し、失敗時は wx.FileDialog にフォールバック
 - **ドラッグ&ドロップ対応**: Windows エクスプローラーや Linux ファイルマネージャーからファイルをテキストフィールドへ直接ドロップ可能
 - 今後拡張しやすいシンプルな構造

## 使い方 (ローカル)
uv 利用前提の仮想環境は不要ですが、既存仮想環境を使う場合は `source .venv/bin/activate` を実行してください。

Tkinter 版:
```bash
uv run app.py
```
wxPython 版:
```bash
uv run wx_app.py
```
## 使い方 (Docker)
X11 の表示をホストへ転送して GUI を表示します。
Linux デスクトップ環境を前提としています。

1. X11 へのアクセス許可 (必要な場合)
```bash
xhost +local:docker
```
2. イメージのビルド
```bash
docker build -t py-gui-tool .
```
3. 実行 (デフォルト: wxPython)
```bash
docker run --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  py-gui-tool
```
(Tkinter をコンテナで動かす場合)
```bash
docker run --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  py-gui-tool python app.py
```
(Wayland 環境の場合は XWayland が有効であることを確認してください。)

## 開発メモ
 - 依存ライブラリ: wxPython (Tkinter は標準ライブラリ)
 - パッケージ管理は uv + `pyproject.toml`。新規追加は `uv add パッケージ名` を利用。
 - Windows ネイティブファイルダイアログは `ctypes` のみで実装 (追加依存なし)

### Windows ネイティブファイルダイアログ
`wx_app.py` のログファイル選択は以下の挙動になります:

1. 実行環境が Windows (`sys.platform.startswith('win')`)
2. Win32 API `GetOpenFileNameW` を `ctypes` で呼び出しネイティブ共通ファイルダイアログを表示
3. 例外やキャンセル時は `None`、他 OS では自動的に `wx.FileDialog` にフォールバック

留意点:
- 追加の Python パッケージは不要です (標準 `ctypes` 利用)。
- フィルタは「All Files」と「Log Files (*.log)」を提供しています。
- 複数選択や最近場所ピン留め等の高度機能は未実装ですが、後で `IFileOpenDialog` へ拡張可能です。
- 取得したパスはテキストフィールド表示のみで解析処理は未実装です。

### リモート Windows ファイルダイアログ (Ubuntu から Windows)
`win_dialog_server.py` を Windows 11 マシンで起動し、Ubuntu 上の `wx_app.py` から HTTP 越しにネイティブダイアログを表示してパスを取得できます。

サーバ起動 (Windows 側 PowerShell または CMD):
```bash
python win_dialog_server.py  # デフォルト: 0.0.0.0:5005
```
カスタムバインド:
```bash
set WIN_DIALOG_BIND=127.0.0.1:6000
python win_dialog_server.py
```

クライアント (Ubuntu 側) 環境変数設定例:
```bash
export REMOTE_WIN_DIALOG=192.168.1.20:5005
export REMOTE_WIN_TIMEOUT=30
# Windows ドライブを CIFS などで /mnt/win にマウントしている場合
export REMOTE_WIN_MOUNT_PREFIX=/mnt/win
uv run wx_app.py
```

動作フロー:
1. `wx_app.py` の `_select_file` で最初に `REMOTE_WIN_DIALOG` を参照
2. 設定されていれば `http://<host>/open` に GET
3. Windows 側でネイティブダイアログ表示 → 選択パス JSON 返却
4. `REMOTE_WIN_MOUNT_PREFIX` が設定されていればパスを Linux 用に `/mnt/win/<Drive>/...` に変換
5. 失敗・タイムアウト時は通常のローカルダイアログ (Windows ならネイティブ / 他 OS は wx) にフォールバック

前提:
- ネットワーク疎通 (双方向不要。Ubuntu -> Windows のみ HTTP GET)
- Windows ドライブ内容を Ubuntu から読みたい場合は CIFS などで共有/マウントするか、Samba 有効化

注意:
- 現状認証なし。信頼できるネットワークでのみ使用してください。
- 複数選択・フォルダ選択は未対応 (拡張可能)。
- パス変換はシンプルな `C:\\` → `/mnt/win/C/` の置換であり、UNC や別ドライブマッピングは追加実装が必要。

### ドラッグ&ドロップによるファイル指定
テキストフィールドへファイルエクスプローラー (Windows/Linux) からファイルを直接ドラッグ&ドロップできます。

使い方:
1. `wx_app.py` を起動
2. 「Register Log」ページで「Select Log File」ボタン下のテキストフィールドにファイルをドロップ
3. ファイルパスが自動入力されます

対応環境:
- Windows: エクスプローラーからのドロップ
- Linux: Nautilus, Dolphin, Thunar などの標準ファイルマネージャー
- macOS: Finder (wxPython がインストールされている場合)

## パッケージ管理 (uv)
本プロジェクトは `uv` に移行しました。`pyproject.toml` で依存を管理します。

### uv インストール (Linux/macOS)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
exec $SHELL -l   # PATH 反映
```
Windows (PowerShell):
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

### 依存同期
```bash
uv sync            # pyproject.toml を読み取りインストール
uv sync --frozen   # uv.lock がある場合ロックを厳守
```

### 依存追加/更新
```bash
uv add wxPython==4.2.1      # 追加
uv remove パッケージ名       # 削除
uv lock                     # uv.lock 再生成
```

### 実行
```bash
uv run wx_app.py
```
`uv run` は隔離された環境で実行するため、従来の仮想環境切替は不要です。

### 環境情報確認
```bash
uv pip list
uv tree
```

## トラブルシュート (wx import 失敗時)
- 依存未同期: `uv sync`
- ネイティブ依存不足 (GTK エラー等): 以下を Debian/Ubuntu で追加
  ```bash
  sudo apt-get install -y libgtk-3-0 libgtk-3-dev libjpeg-dev libtiff-dev libpng-dev \
    libgstreamer1.0-0 libgstreamer-plugins-base1.0-0 libwebkit2gtk-4.0-37 tk
  ```
- ロックずれ: `uv lock` → `uv sync --frozen`
- ネットワーク遮断: 社内ミラー利用またはホイール事前取得 (`uv pip download wxPython==4.2.1`).

## GUI 開発反復フロー
1. コード編集 (`wx_app.py`)  
2. `uv sync` (依存変更時のみ)  
3. `uv run wx_app.py` で起動  
4. 画面確認 → 再編集  

ウォッチ&自動再起動例 (任意):
```bash
uv add watchdog
watchmedo auto-restart -p '*.py' -R -- uv run wx_app.py
```

## 開発環境セットアップ (ローカル)
wxPython が import できない場合は以下の手順で環境を整えてください (Debian/Ubuntu 系)。

1. システム依存パッケージのインストール
```bash
sudo apt-get update
sudo apt-get install -y \
  python3-venv python3-dev build-essential \
  libgtk-3-0 libgtk-3-dev libjpeg-dev libtiff-dev libpng-dev \
  libgstreamer1.0-0 libgstreamer-plugins-base1.0-0 libwebkit2gtk-4.0-37
```
2. 仮想環境作成と有効化
```bash
python3 -m venv .venv
source .venv/bin/activate
```
3. Pythonパッケージのインストール
```bash
python -m pip install -U pip wheel setuptools
pip install -r requirements.txt
```
4. インポート確認
```bash
python -c "import wx; print(wx.version())"
```
5. GUI起動確認
```bash
python wx_app.py
```

DISPLAY が設定されていない場合 (SSH 等) は X11 転送を有効にするか、`echo $DISPLAY` が空でないことを確認してください。

## トラブルシュート (wx が import できない)
- `ModuleNotFoundError: No module named 'wx'` → 仮想環境が有効か (`which python` / `python -m site`) を確認し再度 `pip install wxPython`。
- ビルド関連エラー → 上記依存パッケージが揃っているか確認。`libgtk-3-dev` が不足すると GTK 関連のエラーが発生。
- ネットワークエラー (取得失敗) → 企業ネットワーク制限の場合は社内 PyPI ミラー設定かホイールを別環境で取得し `pip install ./wxPython-<whl>`。
- Python バージョン差異 → 可能なら 3.11 系を使用 (wxPython 4.2.1 で安定)。`python --version` で確認。

## GUI 開発の反復手順
1. 変更 (例: `wx_app.py` 修正)
2. 仮想環境有効化: `source .venv/bin/activate`
3. 起動: `python wx_app.py`
4. 画面を確認し閉じる → 再度修正

ホットリロードは標準では無いため、必要なら `watchmedo` など導入を検討 (`pip install watchdog` 後ファイル変更で再起動スクリプト作成)。

## 次の拡張候補
- メニューと設定ダイアログ
- ログ出力/保存機能
- 設定の永続化 (JSON/YAML)

## Git 運用
初期コミット後は機能単位でブランチを切って開発してください。

## ライセンス
必要に応じて後で追加してください。
