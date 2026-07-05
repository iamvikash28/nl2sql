# Natural Language to SQL Chatbot

Ask questions about a database in plain English. An LLM (Gemini) converts
your question into SQL, the app checks the SQL is safe, runs it, and shows
you the results.

```
You: "Show top 10 customers by revenue"
        ↓
Gemini writes: SELECT customer_name, SUM(sales) ... LIMIT 10;
        ↓
App checks it's a safe SELECT-only query
        ↓
App runs it on SQLite and shows you a table
```

---

## 1. Project files

```
nl2sql-chatbot/
├── create_database.py   # generates the sample SQLite database (shop.db)
├── utils.py              # schema reader + SQL safety guard
├── nl_to_sql.py           # prompt engineering + Gemini API call
├── app.py                 # Streamlit chat UI (the actual app)
├── requirements.txt
└── README.md
```

## 2. Setup (5 minutes)

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

## 3. How each piece works

### `create_database.py` — the data
Generates a small but realistic e-commerce database. In a real project
this step doesn't exist — you'd point at your existing database instead.
I kept `customers`, `products`, and `orders` as separate related tables
(not one flat file) on purpose, because that's what makes NL-to-SQL
*interesting* — the model has to write JOINs, not just single-table
SELECTs.

### `utils.py` — schema introspection + safety
Two jobs:

1. **`get_schema()`** reads SQLite's internal `sqlite_master` table to
   list every table and column, and formats it as text. This text gets
   fed into the Gemini prompt so the model always knows the *exact*
   table/column names — it never has to guess ("is it `customer_name`
   or `name`?").

2. **`is_safe_sql()`** is the security layer. This is the part every
   beginner NL-to-SQL tutorial skips, and it's the one that actually
   matters. The rule is simple: **only single, read-only SELECT
   statements are allowed to execute.** Everything else — `DROP`,
   `DELETE`, `UPDATE`, `INSERT`, stacked queries separated by `;`,
   `PRAGMA`, etc. — gets rejected before it ever touches the database.
   The LLM can say whatever it wants; your Python code is the actual
   gatekeeper.

### `nl_to_sql.py` — prompt engineering
This is where "prompt engineering" as a skill actually shows up. The
prompt to Gemini does three things:
- **Grounds it in the real schema** so it doesn't invent table names
- **Constrains the output format** ("SQL only, no markdown, no
  explanation") so the response is directly executable
- **Restricts it to SELECT-only** as a first line of defense (with
  `is_safe_sql()` as the enforced second line)

If you find the model writing wrong SQL for certain questions, this
prompt is the first place to iterate — try adding example question/SQL
pairs (few-shot prompting) if you want to go further.

### `app.py` — the Streamlit UI
Wires it all together as a chat interface:
1. Read the schema (shown in the sidebar so you can see what's queryable)
2. Take the user's question from `st.chat_input`
3. Call `generate_sql()` → get SQL back from Gemini
4. Call `is_safe_sql()` → block anything unsafe
5. Run the query with `pandas.read_sql_query()` and display it with
   `st.dataframe()`
6. Store the conversation in `st.session_state` so history persists
   as you ask more questions

---

## 4. Extending this project

Once this works, natural next steps (each teaches something new):

- **Point it at PostgreSQL instead of SQLite** — swap `sqlite3.connect()`
  for `psycopg2` or `sqlalchemy`. Teaches you connection strings and
  production-grade databases.
- **Add chart generation** — after getting `df`, ask Gemini "should this
  be a bar chart, line chart, or table?" and render with
  `st.bar_chart(df)` accordingly.
- **Add query explanation** — after running the SQL, ask Gemini to
  explain in plain English what the query did and why, in a second
  API call.
- **Few-shot prompting** — add 3-5 example (question → SQL) pairs to
  the prompt in `nl_to_sql.py` for domain-specific databases where
  the model's first guesses are often wrong.
- **Row-level limits** — add a hard `LIMIT` cap in `is_safe_sql()` so
  no query can accidentally return your entire 10-million-row table.

## 5. Skills you practiced by building this

| Skill | Where |
|---|---|
| SQL | Reading/writing SELECT, JOIN, GROUP BY, aggregate functions |
| Prompt engineering | `nl_to_sql.py` — schema grounding, output constraints |
| Database querying | `sqlite3`, `pandas.read_sql_query()` |
| AI integration | Calling the Gemini API via `google-genai` SDK |
| App security | Validating untrusted LLM output before executing it |
| Streamlit | Chat UI, session state, sidebar, dataframes |
