# Interview Question Generator — LLM API Mini Project

**Idea** give a job role → get 10 tailored interview questions with sample answers.

Uses **Groq** — a free, no-credit-card, OpenAI-compatible LLM API.

## Files
- `interview_question_generator.ipynb` — notebook with all the API code, structured-output and parameter experiments, findings, and best practices.
- `interview_question_app.py` — Streamlit app (the customized prompt lives here).
- `.env` — holds your `GROQ_API_KEY` (do **not** commit this).

## Setup
1. Get a free key at https://console.groq.com (Google/GitHub login, no card).
2. Put your key in `.env`:  `GROQ_API_KEY=gsk_...`
3. Run the notebook, or launch the app:  `streamlit run interview_question_app.py`

## Note
Groq is OpenAI-compatible, so the code uses the standard `openai` package
pointed at `https://api.groq.com/openai/v1`. To switch back to OpenAI later,
just remove the `base_url`/`api_key` overrides and use an `OPENAI_API_KEY`.
