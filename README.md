# Natural Language to SQL Chatbot

NL2SQL Chatbot lets anyone query a database by just asking a question — no SQL knowledge needed. Behind the scenes, Gemini generates the query grounded in the real database schema, and a safety layer blocks anything that isn't a read-only SELECT before it can touch the data. Built with Streamlit, SQLite, and the Gemini API.


---

## Project files

```
nl2sql-chatbot/
├── create_database.py   # generates the sample SQLite database (shop.db)
├── utils.py              # schema reader + SQL safety guard
├── nl_to_sql.py           # prompt engineering + Gemini API call
├── app.py                 # Streamlit chat UI (the actual app)
├── requirements.txt
└── README.md
```

## Setup

**Step 1 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 2 — Get a free Gemini API key**
Go to https://aistudio.google.com/apikey, sign in with a Google account,
and click "Create API key". It's free for moderate usage.

**Step 3 — Build the sample database**
```bash
python create_database.py
```
This creates `shop.db` with three tables: `customers`, `products`, `orders`
(60 customers, 48 products, 800 orders — realistic enough to ask interesting
questions).

**Step 4 — Run the app**
```bash
streamlit run app.py
```
Your browser opens automatically. Paste your Gemini API key into the
sidebar, and start asking questions like:
- "Show top 10 customers by revenue"
- "Which product category sells the most?"
- "Total sales by city"
- "How many orders were placed in 2024?"

---

## Skills

|---|---|
| SQL | Reading/writing SELECT, JOIN, GROUP BY, aggregate functions |
| Prompt engineering | `nl_to_sql.py` — schema grounding, output constraints |
| Database querying | `sqlite3`, `pandas.read_sql_query()` |
| AI integration | Calling the Gemini API via `google-genai` SDK |
| App security | Validating untrusted LLM output before executing it |
| Streamlit | Chat UI, session state, sidebar, dataframes |

## Live demo
[nl-sql.streamlit.app](https://nl-sql.streamlit.app)

## 👤 Author

**Vikash Verma**
Aspiring Data Analyst | Excel · SQL · Power BI · Python | E-mail- vikashverma566@gmail.com

---
