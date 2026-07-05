"""
nl_to_sql.py
------------
This is the "prompt engineering" heart of the project: it turns a plain
English question into a SQL query by calling the Gemini API.

The quality of NL-to-SQL depends almost entirely on the prompt. We give
Gemini three things:
  1. The exact database schema (so it doesn't guess table/column names)
  2. Strict formatting rules (SQL only, no explanations, no markdown)
  3. The user's question

Swap MODEL_NAME below if you want a different Gemini model.
"""

from google import genai
from utils import get_schema, clean_sql_response

MODEL_NAME = "gemini-2.5-flash"  # fast + cheap, good for SQL generation


def build_prompt(question: str, schema: str) -> str:
    """
    Constructs the full prompt sent to Gemini.
    This is the "prompt engineering" skill in action — being explicit
    about constraints massively reduces bad output.
    """
    return f"""You are an expert SQLite query generator.

Below is the schema of the database you must query:

{schema}

Rules you MUST follow:
- Write exactly ONE SQL query that answers the user's question.
- Only use SELECT statements. Never write INSERT, UPDATE, DELETE, DROP, or ALTER.
- Only use table and column names that appear in the schema above.
- Use SQLite syntax.
- Do NOT include any explanation, comments, or markdown formatting.
- Return ONLY the raw SQL query, nothing else.

User question: "{question}"

SQL query:"""


def generate_sql(question: str, api_key: str, schema: str = None) -> str:
    """
    Sends the question to Gemini and returns cleaned, ready-to-run SQL.

    Args:
        question: the user's natural language question
        api_key:  Gemini API key
        schema:   optional pre-fetched schema string (avoids re-reading DB)

    Returns:
        A cleaned SQL string (markdown fences stripped).
    """
    if schema is None:
        schema = get_schema()

    prompt = build_prompt(question, schema)

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    raw_sql = response.text
    return clean_sql_response(raw_sql)
