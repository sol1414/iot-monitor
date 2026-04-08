from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import httpx
import pandas as pd
import streamlit as st
from config import ONLINE_THRESHOLD_SEC, LIVE_TEMP_UPDATE_INTERVAL_SEC, DB_SAVE_DETECT_THRESHOLD_SEC, SENSOR_COLUMNS
from api import api_get, SERVER_URL
from charts import render_summary, render_temperature_chart

JST = ZoneInfo("Asia/Tokyo")


def _init_session_state():
    if "last_db_save" not in st.session_state:
        st.session_state["last_db_save"] = {}
    if "prev_temp" not in st.session_state:
        st.session_state["prev_temp"] = {}


st.set_page_config(page_title="豚舎 IoT モニター", layout="wide")
st.title("豚舎 IoT 環境モニター")
_init_session_state()


# ------------------------------------------------------------------ #
# Live Telemetry（10秒ごと自動更新）
# ------------------------------------------------------------------ #
@st.fragment(run_every=LIVE_TEMP_UPDATE_INTERVAL_SEC)
def live_status_panel():
    st.subheader("Live Telemetry")

    try:
        nodes = api_get("/latest")["nodes"]
    except httpx.HTTPError:
        nodes = []

    now_utc = datetime.now(timezone.utc)
    now_jst_str = now_utc.astimezone(JST).strftime("%H:%M:%S")

    # ── DB保存イベントの検知 ──────────────────────────────────────────
    new_db_save = False
    for node in nodes:
        node_id = node["node_id"]
        current_save = node.get("last_db_save")
        prev_save = st.session_state["last_db_save"].get(node_id)

        if current_save and current_save != prev_save:
            if prev_save is not None:  # 初回ロード時は通知しない
                ts_jst = datetime.fromisoformat(current_save).astimezone(JST).strftime("%H:%M:%S")
                st.toast(f"{node_id} のデータを記録しました  ({ts_jst})", icon="✅")
                new_db_save = True
            st.session_state["last_db_save"][node_id] = current_save

    # ── メトリクス表示 ────────────────────────────────────────────────
    if not nodes:
        st.info("接続待機中... Pico 2W からの受信がありません。")
    else:
        cols = st.columns(min(len(nodes), 4))
        for i, node in enumerate(nodes):
            node_id = node["node_id"]
            last_seen = datetime.fromisoformat(node["last_seen"]).astimezone(timezone.utc)
            secs = int((now_utc - last_seen).total_seconds())
            is_online = secs < ONLINE_THRESHOLD_SEC

            temp = node.get("temperature")
            prev_temp = st.session_state["prev_temp"].get(node_id)

            # 温度の変化量を delta として表示
            temp_str = f"{temp:.2f} ℃" if temp is not None else "-- ℃"
            if temp is not None and prev_temp is not None:
                diff = round(temp - prev_temp, 2)
                temp_delta = f"{diff:+.2f} ℃"
                temp_delta_color = "normal"  # 上昇=赤, 下降=青（Streamlit デフォルト）
            else:
                temp_delta = None
                temp_delta_color = "off"

            # prev_temp を今回値で更新
            if temp is not None:
                st.session_state["prev_temp"][node_id] = temp

            if secs < 60:
                ago_str = f"{secs}秒前"
            elif secs < 3600:
                ago_str = f"{secs // 60}分{secs % 60}秒前"
            else:
                ago_str = f"{secs // 3600}時間前"

            with cols[i % len(cols)]:
                status_color = "🟢" if is_online else "🔴"
                status_label = "ONLINE" if is_online else "OFFLINE"

                st.metric(
                    label=f"{status_color} {node_id}  —  {status_label}",
                    value=temp_str,
                    delta=temp_delta,
                    delta_color=temp_delta_color,
                )
                st.caption(f"最終受信: {ago_str}  |  {node['timestamp'][:19]}")

                last_db_save = node.get("last_db_save")
                if last_db_save:
                    save_jst = datetime.fromisoformat(last_db_save).astimezone(JST).strftime("%H:%M:%S")
                    st.caption(f"最終記録: {save_jst}")

    st.caption(f"最終更新: {now_jst_str}  ·  10秒ごとに自動更新")

    # DB保存を検知したらアプリ全体を再実行 → 履歴パネルも即時更新
    if new_db_save:
        st.rerun()


live_status_panel()

st.divider()


# ------------------------------------------------------------------ #
# 履歴データ（DB保存イベント検知時に即時リフレッシュ）
# ------------------------------------------------------------------ #
@st.fragment(run_every=DB_SAVE_DETECT_THRESHOLD_SEC)
def history_panel():
    st.subheader("履歴データ")

    try:
        node_ids = api_get("/nodes")["nodes"]
    except httpx.HTTPError as e:
        st.error(f"サーバーに接続できません: {e}\nURL: {SERVER_URL}")
        return

    if not node_ids:
        st.info("まだ履歴データがありません。初回送信（起動から最大5分）後に表示されます。")
        return

    left, right = st.columns([1, 3])

    with left:
        selected_node = st.selectbox("ノードID", node_ids, key="hist_node")
        dates = api_get(f"/dates/{selected_node}")["dates"]
        if not dates:
            st.warning(f"{selected_node} のデータが見つかりません。")
            return
        selected_date = st.selectbox("日付", dates, key="hist_date")

    rows = api_get(f"/data/{selected_node}/{selected_date}")["data"]
    if not rows:
        st.info("選択した日付のデータがありません。")
        return

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    with right:
        now_str = datetime.now(JST).strftime("%H:%M:%S")
        st.caption(f"**{selected_node}** / {selected_date} — {len(df)} 件  ·  最終更新: {now_str}")

    # サマリーテーブル
    render_summary(df)

    # 温度グラフ
    render_temperature_chart(df)

    # 生データテーブル（最新データが先頭、スクロール表示）
    st.subheader("計測ログ")
    display_df = (
        df[["timestamp"] + SENSOR_COLUMNS]
        .sort_values("timestamp", ascending=False)
        .rename(columns={
            "timestamp": "時刻",
            "temperature": "温度 (℃)",
            "humidity": "湿度 (%)",
            "co2": "CO₂ (ppm)",
            "lux": "照度 (lux)",
        })
        .reset_index(drop=True)
    )
    st.dataframe(display_df, use_container_width=True, height=300)

    # CSV ダウンロード
    csv_data = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="CSV ダウンロード",
        data=csv_data,
        file_name=f"{selected_node}_{selected_date}.csv",
        mime="text/csv",
    )


history_panel()
