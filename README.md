# Python GUI Tool

Tkinter を用いた最小構成の Python GUI ツールです。

## 機能 (初期状態)
- ラベルとカウンタ付きボタン
- 今後拡張しやすいシンプルな構造

## 使い方 (ローカル)
```bash
python app.py
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
3. 実行
```bash
docker run --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  py-gui-tool
```
(Wayland 環境の場合は XWayland が有効であることを確認してください。)

## 開発メモ
- 依存ライブラリは標準ライブラリのみ (Tkinter)
- 拡張する際は `requirements.txt` に追記してください。

## 次の拡張候補
- メニューと設定ダイアログ
- ログ出力/保存機能
- 設定の永続化 (JSON/YAML)

## Git 運用
初期コミット後は機能単位でブランチを切って開発してください。

## ライセンス
必要に応じて後で追加してください。
