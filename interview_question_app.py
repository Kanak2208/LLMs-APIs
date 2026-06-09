import os
import json

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# Load GROQ_API_KEY from the .env file
load_dotenv()

# Groq is OpenAI-compatible: same client, just a different base_url + key.
# Free key (no credit card) from https://console.groq.com
MODEL = "llama-3.3-70b-versatile"  # also: "llama-3.1-8b-instant", "openai/gpt-oss-120b"

# --- The customized prompt: this is what turns a generic chatbot into an --- #
# --- interview-question generator. It asks for exactly 10 Q&A pairs as JSON. -- #
SYSTEM_PROMPT = """You are an experienced hiring manager and technical recruiter.
Your job is to create realistic interview questions for a given job role.

When given a JOB ROLE and a seniority level, produce exactly 10 interview
questions tailored to that role. For each question, also write a concise model
answer (3-5 sentences) that a strong candidate might give.

Requirements:
- Mix the question types: include technical/role-specific, behavioural
  ("Tell me about a time..."), and situational ("What would you do if...") questions.
- Order questions roughly from warm-up to more challenging.
- Match difficulty to the requested seniority level.
- Keep questions clear and free of bias; never ask about age, religion, gender,
  marital status, or other protected characteristics.
- Keep sample answers practical and specific to the role, not generic filler.

Return ONLY a valid JSON object with this exact shape:
{
  "role": "<the job role>",
  "seniority": "<the seniority level>",
  "questions": [
    {"type": "technical|behavioural|situational",
     "question": "<the question>",
     "sample_answer": "<a concise model answer>"}
  ]
}
The "questions" array must contain exactly 10 items. Do not add any text outside the JSON."""


def get_client():
    return OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )


def generate_questions(role, seniority, temperature):
    """Call the Groq Chat Completions API and return parsed JSON."""
    client = get_client()
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Job role: {role}\nSeniority level: {seniority}"},
        ],
        response_format={"type": "json_object"},
        temperature=temperature,
        max_tokens=1600,
    )
    return json.loads(completion.choices[0].message.content)


# ----------------------------- UI ----------------------------- #
st.set_page_config(page_title="Interview Question Generator", page_icon="🎯")
st.title("🎯 Interview Question Generator")
st.caption("Enter a job role and get 10 tailored interview questions with sample answers. Powered by Groq (free).")

with st.sidebar:
    st.header("Settings")
    seniority = st.selectbox(
        "Seniority level",
        ["entry-level", "junior", "mid-level", "senior", "lead"],
        index=2,
    )
   
    st.markdown("---")
    st.markdown("Question_Type: 🔧 technical · 💬 behavioural · 🧩 situational")

role = st.text_input("Job role", placeholder="e.g. Data Analyst, Frontend Developer, Product Manager")

TYPE_ICON = {"technical": "🔧", "behavioural": "💬", "behavioral": "💬", "situational": "🧩"}

if st.button("Generate questions", type="primary"):
    if not role.strip():
        st.warning("Please enter a job role first.")
    elif not os.getenv("GROQ_API_KEY"):
        st.error("No GROQ_API_KEY found. Add it to your .env file (get a free key at console.groq.com).")
    else:
        with st.spinner(f"Generating questions for a {seniority} {role}..."):
            try:
                data = generate_questions(role.strip(), seniority, temperature)
            except Exception as e:
                st.error(f"Something went wrong calling the API: {e}")
                st.stop()

        st.success(f"10 questions for a **{seniority} {data.get('role', role)}**")

        for i, q in enumerate(data.get("questions", []), start=1):
            icon = TYPE_ICON.get(q.get("type", "").lower(), "•")
            st.markdown(f"**{i}. {icon} {q.get('question', '')}**")
            with st.expander("Show sample answer"):
                st.write(q.get("sample_answer", ""))

        # Let the user download the whole set as JSON
        st.download_button(
            "⬇️ Download as JSON",
            data=json.dumps(data, indent=2, ensure_ascii=False),
            file_name=f"interview_questions_{role.strip().replace(' ', '_').lower()}.json",
            mime="application/json",
        )
