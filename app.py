import streamlit as st
import psycopg2
from datetime import datetime
from collections import defaultdict

# Page Configuration
st.set_page_config(page_title="Todo List", layout="centered")

def get_db_connection():
    return psycopg2.connect(st.secrets["postgres"]["connection_url"])

# Sophisticated Suffix Function
def get_ordinal(n):
    # Returns the correct suffix: 1st, 2nd, 3rd, 4th, 21st, 22nd, 23rd, 28th, etc.
    return str(n) + ("th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))

def format_date_pretty(date_obj):
    # Uses the helper function for accurate ordinals
    return f"{get_ordinal(date_obj.day)} {date_obj.strftime('%B, %Y')}"

st.title("📝 Daily Task List")

# --- Add Task Form ---
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
            with conn.cursor() as cur:
                date_str = f"{year}-{months.index(month)+1:02d}-{day:02d}"
                cur.execute("INSERT INTO todos (todo_name, todo_date) VALUES (%s, %s)", (name, date_str))
                conn.commit()
            conn.close()
            st.rerun()

# --- Display Grouped Tasks ---
conn = get_db_connection()
with conn.cursor() as cur:
    cur.execute("SELECT id, todo_name, todo_date, is_finished FROM todos ORDER BY todo_date ASC")
    tasks = cur.fetchall()
conn.close()

grouped_tasks = defaultdict(list)
for task in tasks:
    grouped_tasks[task[2]].append(task)

st.markdown("### Your Schedule")
for date, items in grouped_tasks.items():
    st.markdown(f"**{format_date_pretty(date)}**")
    
    for item in items:
        task_id, todo_name, _, is_finished = item
        
        # Using columns to create layout: Checkbox | Task | Delete
        c1, c2, c3 = st.columns([0.1, 0.8, 0.1])
        
        # Status Checkbox
        new_status = c1.checkbox("", value=is_finished, key=f"check_{task_id}")
        if new_status != is_finished:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("UPDATE todos SET is_finished = %s WHERE id = %s", (new_status, task_id))
                conn.commit()
            conn.close()
            st.rerun()
            
        # Task Name with visual indentation
        c2.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp; {todo_name}")
        
        # Delete Button
        if c3.button("🗑️", key=f"del_{task_id}"):
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("DELETE FROM todos WHERE id = %s", (task_id,))
                conn.commit()
            conn.close()
            st.rerun()
    st.divider()
