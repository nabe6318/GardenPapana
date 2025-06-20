import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import datetime
import AMD_Tools4 as amd

st.title("ぱぱな農園専用気象データ取得アプリ")
st.markdown("気温（TMP）、相対湿度（RH）、下向き長波放射量（DLR）の時別データを可視化します。")

# --- 地名 → 緯度経度リスト ---
locations = {
    "木裏原": (35.804167, 137.93125),
    "柳沢": (35.795833, 137.93125),
    "藤沢川": (35.7875, 137.93125),
    "表木": (35.7875, 137.94375),
    "下小出": (35.795833, 137.94375),
    "沢渡駅": (35.804167, 137.94375),
    "アメダス伊那": (35.829167, 137.95625),
    "中川村下平": (35.6375, 137.94375),
    "中川村大草城跡公園": (35.629167, 137.94375),
    "中川村役場東": (35.6375, 137.95625),
}

# --- 地名選択 ---
place = st.selectbox("地点を選択してください", list(locations.keys()))
lat, lon = locations[place]
st.success(f"選択された地点: {place}（緯度: {lat}, 経度: {lon}）")

# --- 気象要素選択 ---
element = st.selectbox("気象要素を選択してください", options=["TMP", "RH", "DLR"], format_func=lambda x: {
    "TMP": "気温 (TMP)",
    "RH": "相対湿度 (RH)",
    "DLR": "下向き長波放射量 (DLR)"
}[x])

# --- 日付選択 ---
today = datetime.today().date()
col1, col2 = st.columns(2)
start_date = col1.date_input("開始日", today)
end_date = col2.date_input("終了日", today)

# --- 時別タイムドメイン作成 ---
start_str = str(start_date)
end_str = str(end_date)
timedomain = [f"{start_str}T01", f"{end_str}T24"]
lalodomain = [lat, lat, lon, lon]

# --- データ取得 ---
if st.button("気象データを取得"):
    with st.spinner("時別データを取得中..."):
        try:
            obs, tim, lat_arr, lon_arr, name, unit = amd.GetMetDataHourly(element, timedomain, lalodomain, namuni=True)

            # 次元削減
            obs_1d = obs[:, 0, 0]
            tim = pd.to_datetime(tim)

            # 表形式で出力
            df = pd.DataFrame({
                "日時": tim,
                "値": obs_1d,
            })
            st.subheader("データテーブル")
            st.dataframe(df)

            # 折れ線グラフ
            st.subheader("折れ線グラフ")
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.plot(tim, obs_1d, 'b-', label=name)
            ax.set_xlabel("日時")
            ax.set_ylabel(f"{name} [{unit}]")
            ax.set_title(f"{place}：{name}（時別）")
            ax.xaxis.set_major_formatter(md.DateFormatter('%m/%d %Hh'))
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

        except Exception as e:
            st.error(f"データ取得エラー: {e}")
