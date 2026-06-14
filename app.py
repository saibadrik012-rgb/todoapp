import streamlit as st
import psycopg2
from datetime import datetime
from collections import defaultdict

st.set_page_config(page_title="Todo List", layout="centered")

def get_db_connection():
    return psycopg2.connect(st.secrets["postgres"]["connection_url"])

# Helper to format date: "14th June, 2026"
def format_date_pretty(date_obj):
    day = date_obj.day
    suffix = ["th", "st", "nd", "rd"][min(day % 10, 3)] if not 11 <= day <= 13 else "th"
    return date_obj.strftime(f"%d{suffix} %B, %Y")

st.title("📝 Daily Task List")

# 1. Add Task Form
with st.expander("➕ Add a New Task"):
    with st.form("add_todo", clear_on_submit=True):
        name = st.text_input("Task Name")
        col1, col2, col3 = st.columns(3)
        day = col1.number_input("Day", 1, 31, datetime.now().day)
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month = col2.selectbox("Month", months, index=datetime.now().month-1)
        year = col3.number_input("Year", 2020, 2030, datetime.now().year)
        
        if st.form_submit_button("Add Task"):
            conn = get_db_connection()
            cur = conn.cursor()
            date_str = f"{year}-{months.index(month)+1:02d}-{day:02d}"
            cur.execute("INSERT INTO todos (todo_name, todo_date) VALUES (%s, %s)", (name, date_str))
            conn.commit()
            cur.close()
            conn.close()
            st.rerun()

# 2. Display grouped tasks
conn = get_db_connection()
cur = conn.cursor()
cur.execute("SELECT id, todo_name, todo_date, is_finished FROM todos ORDER BY todo_date ASC")
tasks = cur.fetchall()
cur.close()
conn.close()

# Grouping logic
grouped_tasks = defaultdict(list)
for task in tasks:
    grouped_tasks[task[2]].append(task)

st.markdown("### Your Schedule")
for date, items in grouped_tasks.items():
    # Show date only once
    st.markdown(f"**{format_date_pretty(date)}**")
    
    for item in items:
        task_id, todo_name, _, is_finished = item
        
        # Indented row
        c1, c2, c3 = st.columns([0.1, 0.7, 0.2])
        
        # Checkbox for status
        new_status = c1.checkbox("", value=is_finished, key=f"check_{task_id}")
        if new_status != is_finished:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE todos SET is_finished = %s WHERE id = %s", (new_status, task_id))
            conn.commit()
            cur.close()
            conn.close()
            st.rerun()
            
        c2.write(f"&nbsp;&nbsp;&nbsp;&nbsp; {todo_name}")
        
        # Delete button
        if c3.button("🗑️", key=f"del_{task_id}"):
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM todos WHERE id = %s", (task_id,))
            conn.commit()
            cur.close()
            conn.close()
            st.rerun()
    st.divider()
