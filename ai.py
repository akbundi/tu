import tkinter as tk
from tkinter import ttk, messagebox
import requests, json, os

# ================= CONFIG =================
HF_API_KEY = "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"
MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}
DATA_FILE = "student_data.json"

# ================= AI ENGINE =================
def ask_ai(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 600, "temperature": 0.6}
    }
    r = requests.post(API_URL, headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()[0]["generated_text"]

# ================= STUDENT STATE =================
student = {
    "name": "Student",
    "learning_style": "Example-based",
    "xp": 0,
    "level": 1,
    "course": {},
    "current_module": 0,
    "current_lesson": 0,
    "weak_topics": []
}

def load_student():
    global student
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            student = json.load(f)

def save_student():
    with open(DATA_FILE, "w") as f:
        json.dump(student, f, indent=2)

# ================= COURSE GENERATION =================
def generate_course():
    topic = topic_var.get()
    style = style_var.get()

    prompt = f"""
    Create a full beginner-to-intermediate course on "{topic}".
    Output format:
    Course Title:
    Module 1:
      Lesson 1:
      Lesson 2:
    Module 2:
      Lesson 1:
    """

    text = ask_ai(prompt)
    student["course"] = {"raw": text}
    student["current_module"] = 0
    student["current_lesson"] = 0
    save_student()

    output.delete(1.0, tk.END)
    output.insert(tk.END, "📚 COURSE GENERATED\n\n" + text)

# ================= ADAPTIVE LESSON ENGINE =================
def generate_lesson():
    style = student["learning_style"]
    level = student["level"]
    weak = ", ".join(student["weak_topics"]) or "none"

    prompt = f"""
    You are an adaptive AI teacher.
    Student level: {level}
    Learning style: {style}
    Weak topics: {weak}

    Teach the next lesson from this course:
    {student['course']['raw']}

    Make it concise, adaptive, and interactive.
    """

    lesson = ask_ai(prompt)
    output.delete(1.0, tk.END)
    output.insert(tk.END, lesson)

    # Gamification
    student["xp"] += 20
    if student["xp"] >= student["level"] * 100:
        student["level"] += 1

    save_student()
    update_status()

# ================= AI TUTOR =================
def ask_tutor():
    q = question_var.get()
    style = student["learning_style"]

    prompt = f"""
    You are a personal AI tutor.
    Student level: {student['level']}
    Learning style: {style}
    Weak topics: {student['weak_topics']}

    Student question:
    {q}
    """

    ans = ask_ai(prompt)
    output.insert(tk.END, "\n\n🤖 AI Tutor:\n" + ans)

# ================= UI =================
def update_status():
    status.set(
        f"Level {student['level']} | XP {student['xp']} | Style {student['learning_style']}"
    )

load_student()

root = tk.Tk()
root.title("AI-Powered Adaptive Online School")
root.geometry("950x650")

topic_var = tk.StringVar(value="Python Programming")
style_var = tk.StringVar(value=student["learning_style"])
status = tk.StringVar()

ttk.Label(root, text="Course Topic").pack()
ttk.Entry(root, textvariable=topic_var, width=50).pack()

ttk.Label(root, text="Learning Style").pack()
style_box = ttk.Combobox(
    root,
    textvariable=style_var,
    values=["Text-based", "Example-based", "Visual", "Gamified"],
    state="readonly"
)
style_box.pack()

def apply_style():
    student["learning_style"] = style_var.get()
    save_student()
    update_status()

ttk.Button(root, text="Apply Learning Style", command=apply_style).pack(pady=3)
ttk.Button(root, text="Generate Full Course", command=generate_course).pack(pady=5)
ttk.Button(root, text="Start / Next Lesson", command=generate_lesson).pack(pady=5)

output = tk.Text(root, wrap=tk.WORD, height=22)
output.pack(expand=True, fill="both", padx=10)

question_var = tk.StringVar()
ttk.Entry(root, textvariable=question_var, width=70).pack(pady=3)
ttk.Button(root, text="Ask AI Tutor", command=ask_tutor).pack()

ttk.Label(root, textvariable=status).pack(pady=5)
update_status()

root.mainloop()
