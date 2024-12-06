import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import time
import math
import openai

# OpenAI APIキー設定
openai.api_key=  st.secrets[API_kEY] # 自分のAPIキーを設定してください

# タイトル
st.title("タイマー付きマルチタスク課題管理アプリ")

# セッション状態の初期化
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "elapsed_time" not in st.session_state:
    st.session_state.elapsed_time = 0

# タイマーの状態管理
def start_timer():
    st.session_state.timer_running = True

def stop_timer():
    st.session_state.timer_running = False

def reset_timer():
    st.session_state.timer_running = False
    st.session_state.elapsed_time = 0

# タイマーの更新
if st.session_state.timer_running:
    st.session_state.elapsed_time += 1
    time.sleep(1)

# サイドバーで課題の追加
st.sidebar.header("新しい課題を追加")
task_name = st.sidebar.text_input("課題名")
deadline = st.sidebar.date_input("締め切り日", min_value=datetime.now().date())
total_pages = st.sidebar.number_input("課題の総ページ数", min_value=1, step=1)

if st.sidebar.button("課題を追加"):
    st.session_state.tasks.append({
        "name": task_name,
        "deadline": deadline,
        "total_pages": total_pages,
        "remaining_pages": total_pages
    })
    st.sidebar.success("課題を追加しました！")

# タスク一覧の表示と管理
st.header("課題の進捗管理")
progress_data = []
for i, task in enumerate(st.session_state.tasks):
    days_remaining = (task["deadline"] - datetime.now().date()).days
    pages_per_day = math.ceil(task["total_pages"] / days_remaining) if days_remaining > 0 else task["remaining_pages"]

    st.subheader(f"課題 {i+1}: {task['name']}")
    st.write(f"締め切りまで: **{days_remaining}日**")
    st.write(f"1日あたりの目標ページ数: **{pages_per_day}ページ**")
    st.write(f"残りページ数: **{task['remaining_pages']}ページ**")

    # ページ完了ボタン
    if st.button(f"ページ完了！ ({task['name']})"):
        if task["remaining_pages"] > 0:
            task["remaining_pages"] -= 1
            st.success(f"{task['name']}の残りページ数: {task['remaining_pages']}ページ")
        else:
            st.warning(f"{task['name']}はすべて完了しました！")

    # OpenAIコメント生成
    if st.button(f"{task['name']}に関するアドバイスを取得"):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"学生が勉強する課題は「{task['name']}」。残りページ数は{task['remaining_pages']}ページ。締め切りは{task['deadline']}。効果的な学習方法とアドバイスを教えてください。",
            max_tokens=100
        )
        st.info(response.choices[0].text.strip())

    # 課題削除ボタン
    if st.button(f"{task['name']}を削除"):
        st.session_state.tasks.pop(i)
        st.warning(f"{task['name']}を削除しました！")

    # 進捗データの収集
    progress_data.append({
        "課題名": task["name"],
        "進捗率": 100 - (task["remaining_pages"] / task["total_pages"] * 100)
    })

# 進捗グラフの表示
if progress_data:
    st.header("進捗状況")
    progress_df = pd.DataFrame(progress_data)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(progress_df["課題名"], progress_df["進捗率"], color="skyblue")
    ax.set_title("進捗率 (%)")
    ax.set_ylabel("進捗率")
    ax.set_ylim(0, 100)
    st.pyplot(fig)

# タイマーの表示と操作
st.header("タイマー")
timer_minutes, timer_seconds = divmod(st.session_state.elapsed_time, 60)
st.write(f"経過時間: {timer_minutes:02d}:{timer_seconds:02d}")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Start"):
        start_timer()
with col2:
    if st.button("Stop"):
        stop_timer()
with col3:
    if st.button("Reset"):
        reset_timer()

# アナログ時計の描画
st.header("現在の時刻（アナログ時計）")

def draw_clock():
    now = datetime.now()
    hour, minute, second = now.hour % 12, now.minute, now.second

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect('equal')
    ax.axis('off')
    clock_face = plt.Circle((0, 0), 1, color='black', fill=False, lw=2)
    ax.add_artist(clock_face)

    hour_angle = math.radians((hour * 30 + minute * 0.5) - 90)
    minute_angle = math.radians((minute * 6) - 90)
    second_angle = math.radians((second * 6) - 90)

    hour_hand = (0.5 * math.cos(hour_angle), 0.5 * math.sin(hour_angle))
    minute_hand = (0.7 * math.cos(minute_angle), 0.7 * math.sin(minute_angle))
    second_hand = (0.9 * math.cos(second_angle), 0.9 * math.sin(second_angle))

    ax.plot([0, hour_hand[0]], [0, hour_hand[1]], color="black", lw=6)
    ax.plot([0, minute_hand[0]], [0, minute_hand[1]], color="blue", lw=4)
    ax.plot([0, second_hand[0]], [0, second_hand[1]], color="red", lw=2)

    for i in range(12):
        angle = math.radians(i * 30 - 90)
        x, y = math.cos(angle), math.sin(angle)
        ax.text(x * 1.1, y * 1.1, str(i if i != 0 else 12), ha="center", va="center", fontsize=10)

    return fig

st.pyplot(draw_clock())
