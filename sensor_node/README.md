# sensor_node

Pico 2W センサーノード（MicroPython）

## Prerequisites (電子回路)

| 電子部品 | 役割 | 接続先 | 備考 |
|---|---|---|---|
| Raspberry Pi Pico 2W | マイコン（制御） | — | MicroPython で動作 |
| DS18B20（温度センサー） | 温度センシング | データ線 → GP22 | 1-Wire 通信 |
| 抵抗（4.7kΩ） | プルアップ | 3.3V ↔ GP22 間に跨ぐ | 1-Wire に必須 |
| ジャンプワイヤー | 電源供給 | 3.3V ピン → DS18B20 VDD | — |
| ジャンプワイヤー | GND | GND ピン → DS18B20 GND | — |


## セットアップ

```sh
uv sync
```

## デプロイ

```sh
uv run mpremote cp -r src/**/* : + soft-reset
```

## REPL（シリアルログ確認）

```sh
uv run mpremote connect auto repl
```

REPL 接続後:
- `Ctrl+D` — ソフトリセット（`main.py` 再起動）
- `Ctrl+C` — 実行中スクリプトを停止
- `Ctrl+X` — mpremote 終了

## 送信スケジュール
`/sensor_node/config.py`で詳細設定可

| 種別 | エンドポイント | 間隔 | 用途 |
|------|------------|------|------|
| ハートビート | `POST /heartbeat` | 30秒 | Live Telemetry 表示（DB保存なし） |
| データ | `POST /data` | 5分 | 履歴グラフ（DB保存） |
