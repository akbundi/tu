import tkinter as tk
from tkinter import ttk
import json, os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# ================= MODEL CONFIG =================
MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # CPU-safe, instruction-tuned

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

device = 0 if torch.cuda.is_available() else -1

generator = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    device=device,
    max_length=512
)

# ================= STUDENT DATA =================
DATA_FILE = "student_data.json"

student = {
    "name": "Student",
    "learning_style": "Example-based",
    "xp": 0,
    "level": 1,
    "course": "",
    "weak_topics": []
}

# ================= AI FUNCTION =================
def ask_ai(prompt):
    result = generator(
        prompt,
        do_sample=True,
        temperature=0.6,
        top_p=0.9
    )
    return result[0]["generated_text"]

# ================= PERSISTENCE =================
def load_student():
    global student
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            student.update(json.load(f))

def save_student():
    with open(DATA_FILE, "w") as f:
        json.dump(student, f, indent=2)

# ================= COURSE GENERATION =================
def generate_course():
    topic = topic_var.get()

    prompt = f"""
    Create a complete structured course on {topic}.
    Include:
    - Course overview
    - 4 modules
    - 3 lessons per module
    """

    course = ask_ai(prompt)
    student["course"] = course
    student["xp"] += 20
    save_student()

    output.delete(1.0, tk.END)
    output.insert(tk.END, "📚 FULL COURSE GENERATED\n\n" + course)
    update_status()

# ================= ADAPTIVE LESSON =================
def generate_lesson():
    style = student["learning_style"]
    level = student["level"]
    weak = ", ".join(student["weak_topics"]) or "none"

    prompt = f"""
    You are an adaptive AI teacher.

    Student level: {level}
    Learning style: {style}
    Weak topics: {weak}

    Course:
    {student['course']}

    Teach the next lesson with explanations suited to the learning style.
    """

    lesson = ask_ai(prompt)

    student["xp"] += 30
    if student["xp"] >= student["level"] * 100:
        student["level"] += 1

    save_student()

    output.delete(1.0, tk.END)
    output.insert(tk.END, lesson)
    update_status()

# ================= AI TUTOR =================
def ask_tutor():
    question = question_var.get()

    prompt = f"""
    You are a personal AI tutor.

    Student level: {student['level']}
    Learning style: {student['learning_style']}
    Weak topics: {student['weak_topics']}

    Student question:
    {question}
    """

    answer = ask_ai(prompt)
    output.insert(tk.END, "\n\n🤖 AI Tutor:\n" + answer)

# ================= UI HELPERS =================
def apply_style():
    student["learning_style"] = style_var.get()
    save_student()
    update_status()

def update_status():
    status.set(
        f"Level: {student['level']} | XP: {student['xp']} | Style: {student['learning_style']}"
    )

# ================= UI =================
load_student()

root = tk.Tk()
root.title("AI-Powered Adaptive Online School (Local Model)")
root.geometry("950x650")

topic_var = tk.StringVar(value="Python Programming")
style_var = tk.StringVar(value=student["learning_style"])
status = tk.StringVar()

ttk.Label(root, text="Course Topic").pack()
ttk.Entry(root, textvariable=topic_var, width=50).pack()

ttk.Label(root, text="Learning Style").pack()
ttk.Combobox(
    root,
    textvariable=style_var,
    values=["Text-based", "Example-based", "Visual", "Gamified"],
    state="readonly"
).pack()

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
