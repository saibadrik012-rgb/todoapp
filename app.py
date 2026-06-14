import streamlit as st
import psycopg2
from datetime import datetime

st.set_page_config(page_title="Todo List", layout="centered")

def get_db_connection():
    return psycopg2.connect(st.secrets["postgres"]["connection_url"])

# 1. Form to add task
st.title("📝 Daily Task List")
with st.expander("➕ Add a New Task"):
    with st.form("add_todo", clear_on_submit=True):
        name = st.text_input("Task Name")
        col1, col2, col3 = st.columns(3)
        day = col1.number_input("Day", 1, 31, datetime.now().day)
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month = col2.selectbox("Month", months, index=datetime.now().month-1)
        year = col3.number_input("Year", 2020, 2030, datetime.now().year)
        
        if st.form_submit_button("Add"):
            conn = get_db_connection()
            cur = conn.cursor()
            date_str = f"{year}-{months.index(month)+1:02d}-{day:02d}"
            cur.execute("INSERT INTO todos (todo_name, todo_date) VALUES (%s, %s)", (name, date_str))
            conn.commit()
            cur.close()
            conn.close()
            st.rerun()

# 2. Display as a Line-by-Line list
st.markdown("### Upcoming Tasks")
conn = get_db_connection()
cur = conn.cursor()
# Order by date so the list is chronological
cur.execute("SELECT todo_name, todo_date, is_finished FROM todos ORDER BY todo_date ASC")
rows = cur.fetchall()
cur.close()
conn.close()

if not rows:
    st.info("No tasks added yet!")
else:
    for task in rows:
        todo_name, todo_date, is_finished = task
        # Format the line: Date - Status - Name
        status = "✅" if is_finished else "⏳"
        st.markdown(f"""
        <div style="padding: 10px; border-bottom: 1px solid #ccc;">
            <strong>{todo_date}</strong> | {status} {todo_name}
        </div>
        """, unsafe_allow_html=True)
