import streamlit as st
from github import Github
import datetime

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(layout="wide", page_title="Флешка")

# Уменьшаем отступы и заголовки через CSS
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    h1 {font-size: 1.5rem !important; margin-bottom: 0.5rem;}
    .stTabs [data-baseweb="tab-list"] {gap: 10px;}
    .stTabs [data-baseweb="tab"] {height: 40px; white-space: pre-wrap;}
    </style>
    """, unsafe_allow_html=True)

try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = "arsennurzhanuly/TazaLine" 
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
except:
    st.error("Настройте GITHUB_TOKEN!")
    st.stop()

# --- ЛОГИРОВАНИЕ ---
def write_log(user, action, filename):
    now = (datetime.datetime.utcnow() + datetime.timedelta(hours=5)).strftime("%d.%m.%Y %H:%M")
    log_entry = f"[{now}] {user}: {action} -> {filename}\n"
    try:
        c = repo.get_contents("log.txt")
        repo.update_file("log.txt", "Log", c.decoded_content.decode() + log_entry, c.sha)
    except:
        repo.create_file("log.txt", "Log", log_entry)

# --- ВХОД ---
if "auth" not in st.session_state:
    st.session_state.update({"auth": False, "user": "", "to_delete": []})

if not st.session_state["auth"]:
    u = st.text_input("Имя")
    p = st.text_input("Пароль", type="password")
    if st.button("Войти"):
        users = {"Ляззат": "111", "Нуржау": "222"}
        if u in users and p == users[u]:
            st.session_state.update({"auth": True, "user": u})
            st.rerun()
    st.stop()

# --- ИНТЕРФЕЙС ---
st.markdown("<h1>💾 Виртуальная флешка</h1>", unsafe_allow_html=True)

# Загрузка файлов
with st.sidebar:
    st.write(f"👤 {st.session_state['user']}")
    uploaded_files = st.file_uploader("Загрузить файлы", accept_multiple_files=True, label_visibility="collapsed")
    if uploaded_files:
        if st.button("🚀 Загрузить все"):
            for f in uploaded_files:
                try:
                    repo.create_file(f.name, "Add", f.read())
                    write_log(st.session_state["user"], "ЗАГРУЗИЛ", f.name)
                    st.toast(f"✅ {f.name}")
                except:
                    st.toast(f"❌ {f.name} (уже есть)")
            st.rerun()
    if st.button("Выйти"):
        st.session_state["auth"] = False
        st.rerun()

# --- ТАБЛИЦА ФАЙЛОВ ---
try:
    all_f = repo.get_contents("")
    files = [f for f in all_f if f.name not in ["app.py", "requirements.txt", "README.md", "log.txt"]]
    
    cats = {"📊 Excel": [".xlsx", ".xls", ".csv"], "📝 Word/PDF": [".docx", ".pdf", ".txt"], "🖼 Фото": [".jpg", ".png", ".jpeg"], "📦 Прочее": []}
    tabs = st.tabs(list(cats.keys()))

    for i, tab in enumerate(tabs):
        with tab:
            exts = list(cats.values())[i]
            if i == 3: # Прочее
                cat_files = [f for f in files if not any(f.name.lower().endswith(e) for e in [x for s in cats.values() for x in s])]
            else:
                cat_files = [f for f in files if any(f.name.lower().endswith(e) for e in exts)]

            if not cat_files:
                st.info("Пусто")
            else:
                # Массовое удаление (Форма)
                with st.form(key=f"form_{i}"):
                    # Шапка таблицы
                    h1, h2, h3, h4 = st.columns([0.1, 0.5, 0.2, 0.2])
                    h1.write("🔘")
                    h2.write("Имя файла")
                    h3.write("Дата")
                    h4.write("Скачать")
                    st.divider()

                    selected_files = []
                    for f in cat_files:
                        c1, c2, c3, c4 = st.columns([0.1, 0.5, 0.2, 0.2])
                        if c1.checkbox("", key=f"check_{f.name}"):
                            selected_files.append(f)
                        
                        c2.write(f.name)
                        
                        commit = repo.get_commits(path=f.path)[0]
                        dt = commit.commit.author.date + datetime.timedelta(hours=5)
                        c3.write(dt.strftime("%d.%m %H:%M"))
                        
                        c4.link_button("📥", f.download_url)
                    
                    st.divider()
                    if st.form_submit_button("🗑 Удалить выбранные", type="primary"):
                        if not selected_files:
                            st.toast("⚠️ Ничего не выбрано")
                        else:
                            for sf in selected_files:
                                repo.delete_file(sf.path, "Del", sf.sha)
                                write_log(st.session_state["user"], "УДАЛИЛ", sf.name)
                            st.toast(f"🗑 Удалено объектов: {len(selected_files)}")
                            st.rerun()

except Exception as e:
    st.error(f"Ошибка: {e}")
