import streamlit as st
import datetime
from PIL import Image, ImageDraw
import time
import openai

# Set OpenAI API key
openai.api_key = "your_openai_api_key"

# Function to calculate pages per day
def calculate_pages_per_day(deadline, total_pages):
    today = datetime.date.today()
    days_left = (deadline - today).days
    if days_left > 0:
        return total_pages / days_left
    return total_pages

# Function to generate study comment
def generate_study_comment():
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt="What should I focus on while studying to maximize my efficiency?",
        max_tokens=50
    )
    return response.choices[0].text.strip()

# Draw analog timer
def draw_timer(progress, size=200):
    image = Image.new('RGB', (size, size), 'white')
    draw = ImageDraw.Draw(image)
    center = size // 2
    radius = size // 2 - 10

    draw.ellipse((10, 10, size-10, size-10), outline='black', width=2)
    angle = int(progress * 360)
    draw.pieslice((10, 10, size-10, size-10), start=-90, end=-90 + angle, fill='lightblue')

    return image

# Streamlit UI
st.title("Study Timer and Task Manager")

# Task input
st.header("Task Input")
task_count = st.number_input("Number of tasks:", min_value=1, step=1)
tasks = []

for i in range(task_count):
    st.subheader(f"Task {i+1}")
    deadline = st.date_input(f"Deadline for Task {i+1}:", min_value=datetime.date.today())
    pages = st.number_input(f"Total pages for Task {i+1}:", min_value=1, step=1)
    tasks.append((deadline, pages))

# Display tasks and calculate pages per day
st.header("Tasks Overview")
for i, (deadline, pages) in enumerate(tasks):
    pages_per_day = calculate_pages_per_day(deadline, pages)
    st.write(f"Task {i+1}: Deadline {deadline}, Total Pages {pages}, Pages per day: {pages_per_day:.2f}")

# Analog timer
st.header("Analog Timer")
progress = st.slider("Set timer progress (0% to 100%):", min_value=0, max_value=100, step=1) / 100
image = draw_timer(progress)
st.image(image, caption="Timer", use_column_width=False)

# Timer controls
st.header("Timer Controls")
start = st.button("Start")
stop = st.button("Stop")
reset = st.button("Reset")

if start:
    st.write("Timer started.")
elif stop:
    st.write("Timer stopped.")
elif reset:
    st.write("Timer reset.")

# Page progress
st.header("Task Progress")
task_progress = []

for i, (deadline, pages) in enumerate(tasks):
    st.subheader(f"Task {i+1}")
    completed_pages = st.number_input(f"Pages completed for Task {i+1}:", min_value=0, max_value=pages, step=1)
    remaining_pages = pages - completed_pages
    task_progress.append((completed_pages, remaining_pages))
    st.write(f"Remaining pages for Task {i+1}: {remaining_pages}")

# Generate study comment
if st.button("Get Study Advice"):
    comment = generate_study_comment()
    st.write("Study Advice:", comment)
