"""
app.py
------
Streamlit UI for the Natural Language to SQL chatbot.

Flow on every user message:
  1. Take the question typed in the chat box
  2. Send it + DB schema to Gemini -> get back SQL text
  3. Validate the SQL is a safe, read-only SELECT
  4. Run it against SQLite with pandas
  5. Display: the generated SQL, the result table, and any errors

Run with:
    streamlit run app.py
"""

import sqlite3
import pandas as pd
import streamlit as st

from utils import get_schema, is_safe_sql, DB_PATH
from nl_to_sql import generate_sql

st.set_page_config(page_title="NL to SQL Chatbot", page_icon="🗄️", layout="wide")

# ---------------------------------------------------------------------------
# Sidebar: API key + schema preview
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Setup")

    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        help="Get a free key at https://aistudio.google.com/apikey",
        value=st.session_state.get("api_key", ""),
    )
    st.session_state["api_key"] = api_key

    st.divider()
    st.subheader("📋 Database Schema")
    try:
        schema_text = get_schema(DB_PATH)
        st.code(schema_text, language="text")
    except Exception as e:
        schema_text = None
        st.error(f"Could not read database: {e}")
        st.info("Run `python create_database.py` first.")

    st.divider()
    st.subheader("💡 Try asking")
    st.markdown(
        "- Show top 10 customers by revenue\n"
        "- Which product category sells the most?\n"
        "- Total sales by city\n"
        "- Top 5 best selling products\n"
        "- How many orders were placed in 2024?\n"
        "- Average order value by customer"
    )

st.title("🗄️ Natural Language to SQL Chatbot")
st.caption("Ask questions about the shop database in plain English. Powered by Gemini.")

# ---------------------------------------------------------------------------
# Chat history (stored in Streamlit's session state so it persists
# across reruns within the same browser session)
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay previous turns
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sql" in msg:
            st.code(msg["sql"], language="sql")
        if "df" in msg and msg["df"] is not None:
            st.dataframe(msg["df"], use_container_width=True)

# ---------------------------------------------------------------------------
# Handle a new question
# ---------------------------------------------------------------------------
question = st.chat_input("Ask a question about the data...")

if question:
    # Show the user's message immediately
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        if not api_key:
            error_msg = "⚠️ Please enter your Gemini API key in the sidebar first."
            st.warning(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

        elif schema_text is None:
            error_msg = "⚠️ Database not found. Run `python create_database.py` first."
            st.warning(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

        else:
            # Step 1: Generate SQL
            with st.spinner("Generating SQL..."):
                try:
                    sql = generate_sql(question, api_key, schema=schema_text)
                except Exception as e:
                    sql = None
                    st.error(f"❌ Gemini API error: {e}")
                    st.session_state.messages.append(
                        {"role": "assistant", "content": f"Gemini API error: {e}"}
                    )

            if sql:
                # Step 2: Safety check BEFORE execution
                safe, reason = is_safe_sql(sql)

                if not safe:
                    st.error(f"🚫 Blocked unsafe query: {reason}")
                    st.code(sql, language="sql")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"🚫 Blocked unsafe query: {reason}",
                        "sql": sql,
                    })
                else:
                    st.markdown("Here's the SQL I generated:")
                    st.code(sql, language="sql")

                    # Step 3: Execute against SQLite
                    try:
                        conn = sqlite3.connect(DB_PATH)
                        df = pd.read_sql_query(sql, conn)
                        conn.close()

                        if df.empty:
                            st.info("Query ran successfully but returned no rows.")
                        else:
                            st.dataframe(df, use_container_width=True)

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "Here's the SQL I generated:",
                            "sql": sql,
                            "df": df,
                        })
                    except Exception as e:
                        st.error(f"❌ SQL execution error: {e}")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"❌ SQL execution error: {e}",
                            "sql": sql,
                        })

# Clear chat button
if st.session_state.messages:
    if st.sidebar.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()
