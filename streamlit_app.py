import streamlit as st
from datetime import datetime
import math
import matplotlib.pyplot as plt
import time

# アプリのタイトル
st.title("リアルタイムアナログ時計")

# アナログ時計を描画する関数
def draw_clock():
    now = datetime.now()
    hour, minute, second = now.hour % 12, now.minute, now.second

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.axis("off")

    # 時計の円
    clock_face = plt.Circle((0, 0), 1, color="black", fill=False, lw=2)
    ax.add_artist(clock_face)

    # 針の長さ
    hour_length = 0.5
    minute_length = 0.7
    second_length = 0.9

    # 針の角度計算
    hour_angle = math.radians((hour * 30 + minute * 0.5) - 90)
    minute_angle = math.radians((minute * 6) - 90)
    second_angle = math.radians((second * 6) - 90)

    # 時計の針
    ax.plot([0, hour_length * math.cos(hour_angle)], [0, hour_length * math.sin(hour_angle)], color="black", lw=6)
    ax.plot([0, minute_length * math.cos(minute_angle)], [0, minute_length * math.sin(minute_angle)], color="blue", lw=4)
    ax.plot([0, second_length * math.cos(second_angle)], [0, second_length * math.sin(second_angle)], color="red", lw=2)

    # 時間の数字
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        x, y = math.cos(angle), math.sin(angle)
        ax.text(x * 1.1, y * 1.1, str(i if i != 0 else 12), ha="center", va="center", fontsize=10)

    return fig

# セッションステートで動作状態を管理
if "running" not in st.session_state:
    st.session_state.running = False

# スタートボタン
if st.button("スタート"):
    st.session_state.running = True

# ストップボタン
if st.button("ストップ"):
    st.session_state.running = False

# 時計の表示領域
clock_placeholder = st.empty()

# タイマーの更新
while st.session_state.running:
    with clock_placeholder.container():
        fig = draw_clock()
        st.pyplot(fig)
    time.sleep(1)
