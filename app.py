import streamlit as st
import psycopg2
from streamlit_calendar import calendar
from datetime import datetime

# Set page layout
st.set_page_config(page_title="My Todo Calendar", layout="centered")

# Initialize DB connection
def get_db_connection():
    return psycopg2.connect(st.secrets["postgres"]["connection_url"])

# Helper to ensure table exists
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            todo_name TEXT NOT NULL,
            todo_date DATE NOT NULL,
            is_finished BOOLEAN DEFAULT FALSE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

st.title("📅 Task Calendar")
st.markdown("---")

# Input Form in an expander for a cleaner look
with st.expander("➕ Add a New Task"):
    with st.form("add_todo", clear_on_submit=True):
        name = st.text_input("Task Name")
        col1, col2, col3 = st.columns(3)
        day = col1.number_input("Day", 1, 31, datetime.now().day)
        
        # Month Dropdown
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_name = col2.selectbox("Month", months)
        month = months.index(month_name) + 1
        
        year = col3.number_input("Year", 2020, 2030, datetime.now().year)
        
        if st.form_submit_button("Save Task"):
            conn = get_db_connection()
            cur = conn.cursor()
            date_str = f"{year}-{month:02d}-{day:02d}"
            cur.execute("INSERT INTO todos (todo_name, todo_date) VALUES (%s, %s)", (name, date_str))
            conn.commit()
            cur.close()
            conn.close()
            st.rerun()

# Fetch and Display
conn = get_db_connection()
cur = conn.cursor()
cur.execute("SELECT todo_name, todo_date, is_finished FROM todos")
rows = cur.fetchall()
cur.close()
conn.close()

calendar_events = [{
    "title": f"{'✅' if row[2] else '⏳'} {row[0]}",
    "start": str(row[1]),
    "allDay": True
} for row in rows]

st.markdown("### Your Schedule")
calendar(events=calendar_events, options={"initialView": "dayGridMonth"})
