import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from config import SENSOR_COLUMNS, THRESHOLDS


def render_summary(df: pd.DataFrame):
    """センサごとの最高・最低・平均・閾値逸脱時間のサマリーテーブルを表示する"""
    available = [c for c in SENSOR_COLUMNS if c in df.columns and df[c].notna().any()]
    rows = []
    for col in available:
        series = df[col].dropna()
        thr = THRESHOLDS.get(col, {})
        over_min = (series < thr["min"]).sum() * 5 if "min" in thr else 0
        over_max = (series > thr["max"]).sum() * 5 if "max" in thr else 0
        rows.append({
            "センサ": col,
            "最高値": round(series.max(), 2),
            "最低値": round(series.min(), 2),
            "平均値": round(series.mean(), 2),
            "下限逸脱[分]": int(over_min),
            "上限逸脱[分]": int(over_max),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True)


def render_temperature_chart(df: pd.DataFrame):
    """温度の折れ線グラフを閾値ラインとともに表示する"""
    if "temperature" not in df.columns or not df["temperature"].notna().any():
        return

    st.subheader("温度（℃）")
    thr = THRESHOLDS.get("temperature", {})
    thr_max = thr.get("max")
    thr_min = thr.get("min")
    fig = go.Figure()

    mask_over = df["temperature"] > thr_max if thr_max is not None else pd.Series(False, index=df.index)
    mask_under = df["temperature"] < thr_min if thr_min is not None else pd.Series(False, index=df.index)

    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["temperature"],
        mode="lines+markers", name="温度",
        line=dict(color="#2196F3"),
        marker=dict(
            color=["red" if (o or u) else "#2196F3"
                   for o, u in zip(mask_over, mask_under)],
            size=6
        )
    ))
    if thr_max is not None:
        fig.add_hline(y=thr_max, line_dash="dash", line_color="red",
                      annotation_text=f"上限 {thr_max}℃")
    if thr_min is not None:
        fig.add_hline(y=thr_min, line_dash="dash", line_color="blue",
                      annotation_text=f"下限 {thr_min}℃")

    fig.update_layout(xaxis_title="時刻", yaxis_title="℃", height=350)
    st.plotly_chart(fig, use_container_width=True)
