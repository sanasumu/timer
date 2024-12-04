import streamlit as st
import time
from datetime import timedelta
import threading

# OpenAI APIのセットアップ
import openai
openai.api_key = "your_openai_api_key"  # ChatGPT APIキーをここに入力

# タイマーの進行を表示する関数
def start_timer(duration, subject, content):
    """指定された時間でタイマーを開始し、進行状況を表示"""
    start_time = time.time()
    end_time = start_time + duration
    while time.time() < end_time:
        elapsed_time = time.time() - start_time
        time_left = int(end_time - time.time())
        minutes, seconds = divmod(time_left, 60)
        st.session_state.timer_status[subject] = f"{minutes:02}:{seconds:02}"
        time.sleep(1)
        if st.session_state.stop_flag.get(subject, False):
            st.session_state.timer_status[subject] = "Stopped"
            break

    if not st.session_state.stop_flag.get(subject, False):
        st.session_state.timer_status[subject] = "Time's up!"

# チャットGPTにメッセージを送信して、内容に関する説明を取得する関数
def get_chatgpt_response(subject, content):
    prompt = f"私は{subject}の勉強をしています。内容は{content}です。教えてください。"
    response = openai.Completion.create(
        engine="text-davinci-003",  # または利用可能な最新のエンジンを使用
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# アプリのメイン部分
def main():
    st.title("学習タイマーアプリ")

    # 複数のタイマー設定のためのリスト
    if 'timer_data' not in st.session_state:
        st.session_state.timer_data = []

    if 'timer_status' not in st.session_state:
        st.session_state.timer_status = {}

    if 'stop_flag' not in st.session_state:
        st.session_state.stop_flag = {}

    # タイマー設定の入力
    st.subheader("新しいタイマーを追加")
    duration = st.number_input("学習時間 (分)", min_value=1, max_value=120, value=30)
    subject = st.text_input("教科 (例: 数学)")
    content = st.text_input("内容 (例: 二次関数)")

    if st.button("タイマーを追加"):
        # タイマー設定をセッション状態に追加
        if subject and content:
            st.session_state.timer_data.append({
                'subject': subject,
                'content': content,
                'duration': duration * 60  # 分を秒に変換
            })

            st.success(f"タイマーを追加しました: {subject} - {content}, {duration}分")

    # 追加されたタイマーの表示と開始
    st.subheader("設定されたタイマー")
    for timer in st.session_state.timer_data:
        subject = timer['subject']
        content = timer['content']
        duration = timer['duration']

        # タイマーの状態表示
        st.write(f"教科: {subject}, 内容: {content}, 学習時間: {timedelta(seconds=duration)}")
        if subject in st.session_state.timer_status:
            st.write(f"進行状況: {st.session_state.timer_status[subject]}")

        # タイマーを開始するボタン
        if st.button(f"タイマー開始: {subject}", key=f"start_{subject}"):
            st.session_state.stop_flag[subject] = False  # 停止フラグをリセット
            threading.Thread(target=start_timer, args=(duration, subject, content)).start()

        # タイマー停止ボタン
        if st.button(f"タイマー停止: {subject}", key=f"stop_{subject}"):
            st.session_state.stop_flag[subject] = True  # 停止フラグを立てる

        # ChatGPTによるアドバイスの表示
        if st.button(f"{subject}に関するアドバイスを取得", key=f"advice_{subject}"):
            with st.spinner('ChatGPTからのアドバイスを取得中...'):
                advice = get_chatgpt_response(subject, content)
                st.write(f"ChatGPTのアドバイス: {advice}")

if __name__ == "__main__":
    main()
