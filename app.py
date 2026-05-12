import streamlit as st
from github import Github
import datetime

# --- ИНИЦИАЛИЗАЦИЯ ---
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = "arsennurzhanuly/TazaLine" 
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
except:
    st.error("Настройте GITHUB_TOKEN в Secrets!")
    st.stop()

# --- ФУНКЦИЯ ЛОГИРОВАНИЯ ---
def write_log(user, action, filename):
    now = (datetime.datetime.utcnow() + datetime.timedelta(hours=5)).strftime("%d.%m.%Y %H:%M")
    log_entry = f"[{now}] Пользователь {user}: {action} -> {filename}\n"
    log_file = "log.txt"
    try:
        contents = repo.get_contents(log_file)
        new_content = contents.decoded_content.decode() + log_entry
        repo.update_file(log_file, "Update log", new_content, contents.sha)
    except:
        repo.create_file(log_file, "Initial log", log_entry)

# --- АВТОРИЗАЦИЯ ---
if "auth" not in st.session_state:
    st.session_state = {"auth": False, "user": ""}

if not st.session_state["auth"]:
    st.markdown("<h3 style='text-align: center;'>🔐 Вход в систему</h3>", unsafe_allow_html=True)
    u = st.text_input("Логин (Имя)")
    p = st.text_input("Пароль", type="password")
    if st.button("Войти", use_container_width=True):
        users = {"Ляззат": "111", "Нуржау": "222"} # ПАРОЛИ ТУТ
        if u in users and p == users[u]:
            st.session_state["auth"] = True
            st.session_state["user"] = u
            st.rerun()
        else:
            st.error("Ошибка доступа")
    st.stop()

# --- ИНТЕРФЕЙС ---
st.set_page_config(layout="wide") # Делает сайт широким и компактным
st.sidebar.write(f"👤 Пользователь: {st.session_state['user']}")
if st.sidebar.button("Выйти"):
    st.session_state["auth"] = False
    st.rerun()

st.title("💾 Виртуальная флешка")

# Блок загрузки
with st.expander("📤 Загрузить новые файлы"):
    uploaded_files = st.file_uploader("Выберите файлы", accept_multiple_files=True)
    if uploaded_files:
        if st.button("🚀 Начать массовую загрузку"):
            for f in uploaded_files:
                try:
                    repo.create_file(f.name, f"Add {f.name}", f.read())
                    write_log(st.session_state["user"], "ЗАГРУЗИЛ", f.name)
                    st.success(f"Загружен: {f.name}")
                except:
                    st.error(f"Ошибка: {f.name} (возможно, уже есть)")
            st.rerun()

st.divider()

# --- СОРТИРОВКА ПО ПАПКАМ ---
try:
    all_files = repo.get_contents("")
    files = [f for f in all_files if f.name not in ["app.py", "requirements.txt", "README.md", ".gitignore", "database.csv", "log.txt"]]
    
    # Категории
    cats = {
        "📊 Excel": [".xlsx", ".xls", ".csv"],
        "📝 Word/PDF": [".docx", ".doc", ".pdf", ".txt"],
        "🖼 Фото": [".jpg", ".png", ".jpeg", ".gif"],
        "📦 Прочее": []
    }

    tab_titles = list(cats.keys())
    tabs = st.tabs(tab_titles)

    for i, tab in enumerate(tabs):
        with tab:
            current_cat_ext = list(cats.values())[i]
            # Фильтруем файлы для этой вкладки
            if tab_titles[i] == "📦 Прочее":
                cat_files = [f for f in files if not any(f.name.lower().endswith(e) for e in [ex for sub in cats.values() for ex in sub])]
            else:
                cat_files = [f for f in files if any(f.name.lower().endswith(e) for e in current_cat_ext)]

            if not cat_files:
                st.info("В этой папке пусто")
            else:
                # Отображение компактной сеткой
                cols = st.columns(4) # 4 файла в ряд для компактности
                for idx, f in enumerate(cat_files):
                    with cols[idx % 4]:
                        st.markdown(f"<p style='font-size:14px; margin-bottom:0;'><b>{f.name[:20]}</b></p>", unsafe_allow_html=True)commit = repo.get_commits(path=f.path)[0]
                        dt = commit.commit.author.date + datetime.timedelta(hours=5)
                        st.caption(f"{dt.strftime('%d.%m %H:%M')}")
                        
                        # Компактные кнопки
                        b_col1, b_col2 = st.columns(2)
                        b_col1.link_button("📥", f.download_url)
                        if b_col2.button("🗑", key=f"del_{f.name}"):
                            repo.delete_file(f.path, f"Del {f.name}", f.sha)
                            write_log(st.session_state["user"], "УДАЛИЛ", f.name)
                            st.rerun()
                        st.markdown("<br>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Ошибка: {e}")

# Просмотр логов (только для информации)
if st.sidebar.checkbox("Показать историю действий"):
    try:
        log_data = repo.get_contents("log.txt").decoded_content.decode()
        st.sidebar.text_area("Логи", log_data, height=200)
    except:
        st.sidebar.write("Логи пока пусты")
                    
