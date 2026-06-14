import streamlit as st
import psycopg2

# Access the connection string from secrets
def get_db_connection():
    # Streamlit reads the string directly from the secret
    return psycopg2.connect(st.secrets["postgres"]["connection_url"])
st.set_page_config(page_title="Todo Calendar", layout="wide")
st.title("📅 Todo Calendar App")

# Input Form
with st.form("add_todo"):
    name = st.text_input("Todo Name")
    col1, col2, col3 = st.columns(3)
    day = col1.number_input("Day", 1, 31)
    month = col2.number_input("Month", 1, 12)
    year = col3.number_input("Year", 2020, 2030)
    submitted = st.form_submit_button("Add Todo")

    if submitted:
        conn = get_db_connection()
        cur = conn.cursor()
        date_str = f"{year}-{month:02d}-{day:02d}"
        cur.execute("INSERT INTO todos (todo_name, todo_date) VALUES (%s, %s)", (name, date_str))
        conn.commit()
        cur.close()
        conn.close()
        st.success("Added!")

# Fetch and Format Data for Calendar
conn = get_db_connection()
cur = conn.cursor()
cur.execute("SELECT todo_name, todo_date, is_finished FROM todos")
rows = cur.fetchall()
cur.close()
conn.close()

calendar_events = []
for row in rows:
    calendar_events.append({
        "title": f"{'✅' if row[2] else '⏳'} {row[0]}",
        "start": str(row[1]),
        "allDay": True
    })

# Render Calendar
calendar_options = {
    "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,timeGridWeek"},
    "initialView": "dayGridMonth",
}

calendar(events=calendar_events, options=calendar_options)
