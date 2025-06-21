import streamlit as st
import datetime
import json
import os

TASKS_FILE = "tasks.json"

CATEGORY_COLORS = {
    "Uni": "#EB3991",
    "Privat": "#EDC1D9",
    "Sport": "#AEE2FF",
    "Lernen": "#93C6E7"
}

# Lade Aufgaben aus JSON-Datei, wenn vorhanden
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            data = json.load(f)
            for t in data:
                t["date"] = datetime.datetime.strptime(t["date"], "%Y-%m-%d").date()
            return data
    return []

# Speichere Aufgaben in JSON-Datei
def save_tasks(tasks):
    data = []
    for t in tasks:
        task_copy = t.copy()
        task_copy["date"] = task_copy["date"].isoformat()
        data.append(task_copy)
    with open(TASKS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Initialisierung des Session State
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()
if "week_offset" not in st.session_state:
    st.session_state.week_offset = 0

def get_current_week():
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    monday += datetime.timedelta(weeks=st.session_state.week_offset)
    return [monday + datetime.timedelta(days=i) for i in range(7)]

def add_task():
    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input("Titel")
        category = st.selectbox("Kategorie", list(CATEGORY_COLORS.keys()))
        date = st.date_input("Datum", datetime.date.today())
        priority = st.selectbox("Priorität", ["hoch", "mittel", "niedrig"])
        description = st.text_area("Beschreibung (optional)")
        submitted = st.form_submit_button("➕ Aufgabe hinzufügen")

        if submitted:
            if not title.strip():
                st.warning("Bitte einen Titel eingeben.")
                return
            new_task = {
                "title": title.strip(),
                "category": category,
                "date": date,
                "priority": priority,
                "description": description.strip(),
                "done": False
            }
            st.session_state.tasks.append(new_task)
            save_tasks(st.session_state.tasks)
            st.experimental_rerun()  # 🔁 erzwingt Neustart & zeigt neue Aufgabe sofort

def show_week():
    week = get_current_week()
    st.write(f"### Woche: {week[0].strftime('%d.%m.%Y')} - {week[-1].strftime('%d.%m.%Y')}")

    for day in week:
        st.write(f"**{day.strftime('%A, %d.%m.%Y')}**")
        day_tasks = [(i, t) for i, t in enumerate(st.session_state.tasks) if t['date'] == day and not t['done']]

        if not day_tasks:
            st.write("_Keine Aufgaben_")
        else:
            for i, task in day_tasks:
                color = CATEGORY_COLORS.get(task['category'], "#000000")
                with st.container():
                    st.markdown(f"""
                    <div style="
                        border: 1px solid {color};
                        border-radius: 8px;
                        padding: 10px;
                        margin-bottom: 8px;
                        background-color: {color}22;
                    ">
                    """, unsafe_allow_html=True)

                    checked = st.checkbox(
                        f"**{task['category']}**: {task['title']} _(Priorität: {task['priority']})_",
                        value=task['done'],
                        key=f"task-{i}"
                    )
                    if checked != task['done']:
                        st.session_state.tasks[i]['done'] = checked
                        save_tasks(st.session_state.tasks)
                        st.experimental_rerun()  # 🔁 Aufgabe sofort ausblenden

                    if task['description']:
                        st.markdown(
                            f"<div style='font-size:12px; margin-left: 10px; color: {color};'>📝 {task['description']}</div>",
                            unsafe_allow_html=True
                        )
                    st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

# App-Header
st.markdown("# 🎀 TASKLY - *YOUR WEEK, YOUR WAY*")

# Navigation zwischen Wochen
col1, _, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("⬅️ Vorherige Woche"):
        st.session_state.week_offset -= 1
        st.experimental_rerun()
with col3:
    if st.button("Nächste Woche ➡️"):
        st.session_state.week_offset += 1
        st.experimental_rerun()

# Wochenansicht & Aufgabenformular
show_week()
st.markdown("---")
add_task()
