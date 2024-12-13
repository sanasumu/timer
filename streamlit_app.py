import streamlit as st
from datetime import datetime, timedelta
import math
import matplotlib.pyplot as plt
import openai

# OpenAI APIキー（環境変数などで設定することを推奨）
openai.api_key = "your_openai_api_key"

# アプリのタイトル
st.title("課題タイマー Web アプリ")
st.sidebar.header("課題の入力フォーム")

# 課題管理用セッションの初期化
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# 課題の入力フォーム
with st.sidebar.form(key="task_form"):
    task_name = st.text_input("課題名")
    deadline = st.date_input("締め切り日", min_value=datetime.now().date())
    total_pages = st.number_input("課題の総ページ数", min_value=1, step=1)
    add_task = st.form_submit_button("課題を追加")

    if add_task and task_name:
        st.session_state.tasks.append({
            "name": task_name,
            "deadline": deadline,
            "total_pages": total_pages,
            "remaining_pages": total_pages
        })
        st.success(f"課題 '{task_name}' を追加しました！")

# 課題の進行状況の表示
if st.session_state.tasks:
    st.header("課題の進行状況")
    for task in st.session_state.tasks:
        st.subheader(f"課題: {task['name']}")
        
        # 締め切りまでの日数計算
        days_remaining = (task["deadline"] - datetime.now().date()).days
        if days_remaining > 0:
            pages_per_day = math.ceil(task["total_pages"] / days_remaining)
        else:
            pages_per_day = task["remaining_pages"]

        st.write(f"締め切りまでの残り日数: **{days_remaining}日**")
        st.write(f"1日あたりの目標ページ数: **{pages_per_day}ページ**")
        st.write(f"現在の残りページ数: **{task['remaining_pages']}ページ**")
        
        # ページ完了ボタン
        if st.button(f"{task['name']} - ページ完了", key=task["name"]):
            if task["remaining_pages"] > 0:
                task["remaining_pages"] -= 1
                st.success(f"残りページ数: {task['remaining_pages']}ページ")
            if task["remaining_pages"] == 0:
                st.success(f"課題 '{task['name']}' を完了しました！")

# OpenAIを使用した勉強コメントの生成
if st.button("勉強アドバイスを取得"):
    task_summaries = "\n".join([f"- {task['name']} (残り {task['remaining_pages']} ページ, 締め切り {task['deadline']})" for task in st.session_state.tasks])
    prompt = f"""
    以下の課題を考慮して、勉強のアドバイスを提供してください：
    {task_summaries}
    """
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        advice = response.choices[0].text.strip()
        st.info(f"OpenAIからのアドバイス: {advice}")
    except Exception as e:
        st.error(f"OpenAI APIエラー: {e}")

# アナログ時計の表示
st.header("アナログ時計")

def draw_clock():
    now = datetime.now()
    hour, minute, second = now.hour % 12, now.minute, now.second

    # 時計の円
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect('equal')
    ax.axis('off')
    clock_face = plt.Circle((0, 0), 1, color='black', fill=False, lw=2)
    ax.add_artist(clock_face)

    # 針の長さ
    hour_length = 0.5
    minute_length = 0.7
    second_length = 0.9

    # 角度計算（12時基準で回転）
    hour_angle = math.radians((hour * 30 + minute * 0.5) - 90)
    minute_angle = math.radians((minute * 6) - 90)
    second_angle = math.radians((second * 6) - 90)

    # 針の位置
    hour_hand = (hour_length * math.cos(hour_angle), hour_length * math.sin(hour_angle))
    minute_hand = (minute_length * math.cos(minute_angle), minute_length * math.sin(minute_angle))
    second_hand = (second_length * math.cos(second_angle), second_length * math.sin(second_angle))

    # 時計の針を描画
    ax.plot([0, hour_hand[0]], [0, hour_hand[1]], color="black", lw=6)
    ax.plot([0, minute_hand[0]], [0, minute_hand[1]], color="blue", lw=4)
    ax.plot([0, second_hand[0]], [0, second_hand[1]], color="red", lw=2)

    # 時間のマーク
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        x, y = math.cos(angle), math.sin(angle)
        ax.text(x * 1.1, y * 1.1, str(i if i != 0 else 12), ha="center", va="center", fontsize=10)

    return fig

# 時計の描画
st.pyplot(draw_clock())
