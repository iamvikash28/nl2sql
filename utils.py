"""
utils.py
--------
Helper functions shared by app.py:
  1. get_schema()      - reads the DB structure so we can tell Gemini what tables/columns exist
  2. is_safe_sql()      - blocks anything that isn't a read-only SELECT
  3. clean_sql_response()- strips markdown fences Gemini sometimes wraps around SQL
"""

import sqlite3
import re

DB_PATH = "shop.db"

# Only these statement types are ever allowed to run.
# Anything else (INSERT, UPDATE, DELETE, DROP, ALTER, ATTACH, PRAGMA, etc.) is rejected.
FORBIDDEN_KEYWORDS = [
    "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE",
    "TRUNCATE", "REPLACE", "ATTACH", "DETACH", "PRAGMA",
    "VACUUM", "REINDEX", "GRANT", "REVOKE",
]


def get_schema(db_path: str = DB_PATH) -> str:
    """
    Reads all table names + their columns from SQLite and formats them
    as a compact text block. This is what we hand to Gemini so it knows
    the exact table/column names to use (instead of guessing).
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]

    schema_lines = []
    for table in tables:
        cur.execute(f"PRAGMA table_info({table})")
        columns = cur.fetchall()  # (cid, name, type, notnull, default, pk)
        col_desc = ", ".join(f"{c[1]} ({c[2]})" for c in columns)
        schema_lines.append(f"Table: {table}\n  Columns: {col_desc}")

    conn.close()
    return "\n\n".join(schema_lines)


def clean_sql_response(raw_text: str) -> str:
    """
    Gemini often wraps SQL in ```sql ... ``` markdown fences.
    This strips that so we're left with pure SQL text.
    """
    text = raw_text.strip()
    # Remove ```sql or ``` fences
    text = re.sub(r"^```sql\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"```\s*$", "", text)
    return text.strip()


def is_safe_sql(sql: str) -> tuple[bool, str]:
    """
    Validates that the SQL is a single, read-only SELECT statement.
    Returns (is_safe: bool, reason: str).
    """
    stripped = sql.strip().rstrip(";").strip()

    if not stripped:
        return False, "Empty SQL generated."

    # Must start with SELECT (allow leading WITH for CTEs)
    first_word = stripped.split()[0].upper()
    if first_word not in ("SELECT", "WITH"):
        return False, f"Only SELECT queries are allowed. Got statement starting with '{first_word}'."

    # Reject multiple statements (basic stacked-query protection)
    if ";" in stripped:
        return False, "Multiple statements are not allowed."

    # Reject forbidden keywords anywhere in the query
    upper_sql = stripped.upper()
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper_sql):
            return False, f"Forbidden keyword detected: {keyword}"

    return True, "OK"
