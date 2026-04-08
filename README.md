# 豚舎 IoT 環境モニター

```
[Pico 2W] --WiFi--> [Pi 4 : pigfarm-ap]
                     ├── FastAPI  :8000  (センサデータ受信・保存)
                     └── Streamlit:8501  (ダッシュボード)

[Mac/スマホ] --WiFi(pigfarm-ap)--> ブラウザで http://192.168.50.1:8501
```

---

## 1. Pi 4 セットアップ（初回のみ）
> Mac が Pi 4 と同じ Wi-Fi に繋がっている状態かつ、`ansible/inventory/hosts.yaml`を自分用に設定して実行

```sh
cd ansible
uv sync
uv run ansible-playbook -i inventory/hosts.yaml setup-all.yml
```

完了すると Pi 4 に以下が立ち上げる：
- Wi-Fi AP `pigfarm-ap` (パスワード: `pigfarm123`)
- FastAPI サーバー `:8000`（自動起動）
- Streamlit ダッシュボード `:8501`（自動起動）

---

## 2. Pico 2W セットアップ（初回のみ）

```sh
cd sensor_node
uv sync
uv run mpremote cp -r src/**/* : + soft-reset
```

`sensor_node/src/config.py` の `NODE_ID` を台数分変更（node01, node02...）
> 初期設定以降はPICO2Wに電力供給があるタイミングで、すべての処理が自動実行（AP接続 → センシング → DBに記録）

---

## 3. 通常の使い方

1. Mac/スマホを Wi-Fi `pigfarm-ap` に接続
2. ブラウザで `http://192.168.50.1:8501` を開く、または以下のQRコードを読み込む
<img width="450" height="450" alt="qrcode_ifts iot-monito" src="assets/web_qrcode.png" />