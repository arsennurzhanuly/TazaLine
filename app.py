import streamlit as st
from github import Github
import datetime
import re

# --- КОНФИГУРАЦИЯ ---
st.set_page_config(layout="wide", page_title="TazaLine")

st.markdown("""
    <style>
    .block-container {padding-top: 0.5rem; padding-bottom: 0rem;}
    h1 {font-size: 1.2rem !important; margin-bottom: 0.2rem;}
    .stCheckbox {margin-bottom: -15px;}
    .css-10trblm {font-size: 12px;} 
    div[data-testid="stExpander"] {margin-top: -15px;}
    tr, td, th {padding: 2px 5px !important; font-size: 13px !important;}
    </style>
    """, unsafe_allow_html=True)

try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = "arsennurzhanuly/TazaLine" 
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
except:
    st.error("Ошибка токена!")
    st.stop()

# --- ФУНКЦИИ ---
def get_user_for_file(filename):
    try:
        log_content = repo.get_contents("log.txt").decoded_content.decode()
        lines = log_content.split('\n')
        for line in reversed(lines):
            if filename in line and "ЗАГРУЗИЛ" in line:
                match = re.search(r"\] (.*?):", line)
                return match.group(1) if match else "---"
    except: pass
    return "---"

def write_log(user, action, filename):
    now = (datetime.datetime.utcnow() + datetime.timedelta(hours=5)).strftime("%d.%m.%Y %H:%M")
    log_entry = f"[{now}] {user}: {action} -> {filename}\n"
    try:
        c = repo.get_contents("log.txt")
        repo.update_file("log.txt", "Log", c.decoded_content.decode() + log_entry, c.sha)
    except:
        repo.create_file("log.txt", "Log", log_entry)

def upload_with_rename(uploaded_file, user):
    original_name = uploaded_file.name
    name, ext = (original_name.rsplit('.', 1) if '.' in original_name else (original_name, ''))
    ext = '.' + ext if ext else ''
    
    final_name = original_name
    counter = 1
    
    # Проверка на дубликаты и переименование
    all_files = [f.name for f in repo.get_contents("")]
    while final_name in all_files:
        final_name = f"{name}({counter}){ext}"
        counter += 1
        
    repo.create_file(final_name, "Add", uploaded_file.read())
    write_log(user, "ЗАГРУЗИЛ", final_name)
    return final_name

# --- ВХОД ---
if "auth" not in st.session_state:
    st.session_state.update({"auth": False, "user": ""})

if not st.session_state["auth"]:
    c1, c2 = st.columns([1, 3])
    with c1:
        u = st.text_input("Имя")
        p = st.text_input("Пароль", type="password")
        if st.button("Войти", use_container_width=True):
            users = {"Ляззат": "111", "Нуржау": "222"}
            if u in users and p == users[u]:
                st.session_state.update({"auth": True, "user": u})
                st.rerun()
    st.stop()

# --- ШАПКА ---
st.markdown("<h1>💾 TazaLine: Флешка</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.write(f"👤 {st.session_state['user']}")
    up_files = st.file_uploader("Загрузка", accept_multiple_files=True, label_visibility="collapsed")
    if up_files and st.button("🚀 Загрузить"):
        for f in up_files:
            new_name = upload_with_rename(f, st.session_state["user"])
            st.toast(f"✅ {new_name}")
        st.rerun()
    if st.button("Выход"):
        st.session_state["auth"] = False
        st.rerun()

# --- ОСНОВНОЙ КОНТЕНТ ---
try:
    all_f = repo.get_contents("")
    files = [f for f in all_f if f.name not in ["app.py", "requirements.txt", "README.md", "log.txt", "notes.txt"]]
    
    cats = {"📊 Excel": [".xlsx", ".xls", ".csv"], "📝 Word/PDF": [".docx", ".pdf", ".txt"], "🖼 Фото": [".jpg", ".png", ".jpeg"], "📦 Прочее": [], "💬 Заметки": []}
    tabs = st.tabs(list(cats.keys()))

    for i, tab in enumerate(tabs):
        with tab:
            if i == 4: # ЗАМЕТКИ
                try:
                    notes_file = repo.get_contents("notes.txt")
                    current_notes = notes_file.decoded_content.decode()
                except:
                    current_notes = ""
                
                new_note = st.text_area("Текст заметок (общий для всех)", value=current_notes, height=300)
                if st.button("💾 Сохранить текст"):
                    try:
                        repo.update_file("notes.txt", "Update notes", new_note, notes_file.sha)
                    except:
                        repo.create_file("notes.txt", "Init notes", new_note)
                    st.success("Сохранено!")
                continue

            # Фильтрация файлов
            exts = list(cats.values())[i]
            if i == 3: # Прочее
                cat_files = [f for f in files if not any(f.name.lower().endswith(e) for e in [x for s in cats.values() for x in s])]
            else:
                cat_files = [f for f in files if any(f.name.lower().endswith(e) for e in exts)]

            if not cat_files:
                st.info("Пусто")
                continue

            # Разделение на две таблицы (если > 20 файлов)
            split_at = 20
            table_groups = [cat_files[x:x+split_at] for x in range(0, len(cat_files), split_at)]
            
            # Если групп больше 1, показываем их в колонках
            display_cols = st.columns(len(table_groups) if len(table_groups) <= 2 else 2)
            
            for g_idx, group in enumerate(table_groups):
                with display_cols[g_idx % 2]:
                    with st.form(key=f"f_{i}_{g_idx}"):
                        st.markdown("🔘 | Имя файла (скачать) | Дата | Кто")
                        sel = []
                        for f in group:
                            c1, c2, c3, c4 = st.columns([0.1, 0.5, 0.2, 0.2])
                            if c1.checkbox("", key=f"ch_{f.name}"): sel.append(f)
                            c2.markdown(f"[{f.name}]({f.download_url})") # Скачивание по клику на имя
                            
                            commit = repo.get_commits(path=f.path)[0]
                            dt = commit.commit.author.date + datetime.timedelta(hours=5)
                            c3.write(dt.strftime("%d.%m %H:%M"))
                            c4.write(get_user_for_file(f.name))
                        
                        if st.form_submit_button("🗑 Удалить отмеченные", type="primary"):
                            for sf in sel:
                                repo.delete_file(sf.path, "Del", sf.sha)
                                write_log(st.session_state["user"], "УДАЛИЛ", sf.name)
                            st.rerun()

except Exception as e:
    st.error(f"Ошибка: {e}")
