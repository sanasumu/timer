import streamlit as st
from datetime import datetime, date
import math
import matplotlib.pyplot as plt
import openai

# OpenAI APIキー（適宜変更してください）
openai.api_key = "your_openai_api_key"

# セッション管理用
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# サイドバーで課題入力
st.sidebar.header("課題の入力フォーム")
with st.sidebar.form(key="task_form"):
    task_name = st.text_input("課題名")
    deadline = st.date_input("締め切り日", min_value=date.today())
    total_pages = st.number_input("課題の総ページ数", min_value=1, step=1)
    add_task = st.form_submit_button("課題を追加")

    if add_task and task_name:
        st.session_state.tasks.append({
            "name": task_name,
            "deadline": deadline,
            "total_pages": total_pages,
            "remaining_pages": total_pages
        })
        st.sidebar.success(f"課題 '{task_name}' を追加しました！")

# メインコンテンツ
st.title("課題タイマーアプリ")

if st.session_state.tasks:
    for i, task in enumerate(st.session_state.tasks):
        st.subheader(f"課題: {task['name']}")
        days_remaining = (task["deadline"] - date.today()).days
        pages_per_day = math.ceil(task["total_pages"] / days_remaining) if days_remaining > 0 else task["remaining_pages"]
        st.write(f"締め切り: {task['deadline']} （残り {days_remaining} 日）")
        st.write(f"1日あたりの目標ページ数: {pages_per_day} ページ")
        st.write(f"残りページ数: {task['remaining_pages']} ページ")

        if st.button(f"{task['name']} - ページ完了", key=f"task_{i}"):
            if task["remaining_pages"] > 0:
                task["remaining_pages"] -= 1
                st.success(f"'{task['name']}' の残りページ数: {task['remaining_pages']} ページ")
            if task["remaining_pages"] == 0:
                st.success(f"課題 '{task['name']}' 完了！")

# OpenAIによる勉強アドバイス
if st.button("勉強アドバイスを取得"):
    if st.session_state.tasks:
        task_details = "\n".join(
            [f"{task['name']} - 残り {task['remaining_pages']} ページ - 締め切り {task['deadline']}" for task in st.session_state.tasks]
        )
        prompt = f"以下の課題について、勉強を効率的に進めるためのアドバイスを提供してください:\n\n{task_details}"
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=100,
                temperature=0.7
            )
            st.info(f"OpenAIからのアドバイス:\n\n{response.choices[0].text.strip()}")
        except Exception as e:
            st.error(f"OpenAI APIエラー: {e}")
    else:
        st.warning("課題を追加してください！")

# アナログ時計
st.header("アナログ時計")

def draw_clock():
    now = datetime.now()
    hour, minute, second = now.hour % 12, now.minute, now.second

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.axis("off")

    # 円形
    clock_face = plt.Circle((0, 0), 1, color="black", fill=False, lw=2)
    ax.add_artist(clock_face)

    # 針の長さ
    hour_length = 0.5
    minute_length = 0.7
    second_length = 0.9

    # 角度計算
    hour_angle = math.radians((hour * 30 + minute * 0.5) - 90)
    minute_angle = math.radians((minute * 6) - 90)
    second_angle = math.radians((second * 6) - 90)

    # 針を描画
    ax.plot([0, hour_length * math.cos(hour_angle)], [0, hour_length * math.sin(hour_angle)], color="black", lw=6)
    ax.plot([0, minute_length * math.cos(minute_angle)], [0, minute_length * math.sin(minute_angle)], color="blue", lw=4)
    ax.plot([0, second_length * math.cos(second_angle)], [0, second_length * math.sin(second_angle)], color="red", lw=2)

    # 時間の数字
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        x, y = math.cos(angle), math.sin(angle)
        ax.text(x * 1.1, y * 1.1, str(i if i != 0 else 12), ha="center", va="center", fontsize=10)

    return fig

st.pyplot(draw_clock())
