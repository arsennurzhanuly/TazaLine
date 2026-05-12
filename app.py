import streamlit as st
from github import Github
import datetime

# --- НАСТРОЙКИ СТИЛЯ (ФИНАЛЬНЫЙ ТЮНИНГ) ---
st.set_page_config(layout="wide", page_title="TazaLine")

st.markdown("""
    <style>
    /* Позиция заголовка: чуть выше, шрифт +2 */
    .block-container {padding: 4rem 1rem 0.5rem 1rem !important;}
    h1 {
        font-size: 1.6rem !important; 
        margin-bottom: 0.2rem !important; 
        padding-bottom: 0px !important;
        color: #333;
    }
    
    /* Вкладки: прижаты к заголовку */
    .stTabs {margin-top: -10px !important;}
    .stTabs [data-baseweb="tab-list"] {gap: 1px;}
    .stTabs [data-baseweb="tab"] {height: 24px; font-size: 11px !important; padding: 0 8px !important;}
    
    /* Таблица */
    div[data-testid="column"] {gap: 0px !important; padding: 0px !important;}
    .stCheckbox {margin-bottom: -28px !important; margin-top: -12px !important;}
    
    p, div, span, label {
        font-size: 11px !important; 
        line-height: 0.85 !important; 
        margin: 0 !important; 
        padding: 0 !important;
    }
    
    hr {margin: 0.01rem 0 !important; border-top: 1px solid #f9f9f9 !important;}
    
    /* Кнопка скачивания (микро) */
    .stLinkButton a {
        padding: 0px 2px !important;
        height: 14px !important;
        min-height: 14px !important;
        width: 18px !important;
        font-size: 9px !important;
        background-color: transparent !important;
        border: 1px solid #eee !important;
        display: inline-flex !important;
        align-items: center;
        justify-content: center;
    }
    
    [data-testid="stForm"] {padding: 0px !important; border: none !important;}
    </style>
    """, unsafe_allow_html=True)

try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = "arsennurzhanuly/TazaLine" 
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
except:
    st.error("Ошибка ключа GitHub!")
    st.stop()

# --- ФУНКЦИИ ---
@st.cache_data(ttl=15)
def get_all_files():
    # Получаем файлы и сортируем их: новые сверху
    all_f = repo.get_contents("")
    ignore = ["app.py", "requirements.txt", "README.md", "log.txt", "notes.txt", ".gitignore"]
    files = [f for f in all_f if f.name not in ignore]
    # Сортировка по дате последнего коммита (новые вверху)
    return sorted(files, key=lambda x: repo.get_commits(path=x.path)[0].commit.author.date, reverse=True)

@st.cache_data(ttl=15)
def get_file_info(filepath):
    try:
        commits = repo.get_commits(path=filepath)
        last_commit = commits[0]
        dt = last_commit.commit.author.date + datetime.timedelta(hours=5)
        author = "---"
        try:
            log_content = repo.get_contents("log.txt").decoded_content.decode()
            for line in reversed(log_content.split('\n')):
                if filepath in line and "ЗАГРУЗИЛ" in line:
                    author = line.split('] ')[1].split(':')[0]
                    break
        except: pass
        return dt.strftime("%d.%m %H:%M"), author
    except:
        return "--.-- --:--", "---"

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

with st.sidebar:
    st.write(f"👤 {st.session_state['user']}")
    up_files = st.file_uploader("Загрузка", accept_multiple_files=True, label_visibility="collapsed")
    if up_files and st.button("🚀 OK"):
        for f in up_files:
            upload_with_rename(f, st.session_state["user"])
        st.rerun()
    if st.button("Выход"):
        st.session_state["auth"] = False
        st.rerun()

# --- ТАБЛИЦЫ ---
try:
    files = get_all_files()
    
    cats = {"📊 Excel": [".xlsx", ".csv"], "📝 Word/PDF": [".docx", ".pdf", ".txt"], "🖼 Фото": [".jpg", ".png"], "📦 Прочее": [], "💬 Заметки": []}
    tabs = st.tabs(list(cats.keys()))

    for i, tab in enumerate(tabs):
        with tab:
            if i == 4: # Заметки
                try:
                    nf = repo.get_contents("notes.txt")
                    note_text = nf.decoded_content.decode()
                except: note_text = ""
                new_n = st.text_area("Заметки", value=note_text, height=120, label_visibility="collapsed")
                if st.button("💾 Сохранить"):
                    try: repo.update_file("notes.txt", "Upd", new_n, nf.sha)
                    except: repo.create_file("notes.txt", "Init", new_n)
                    st.toast("OK")
                continue

            exts = list(cats.values())[i]
            if i == 3: cat_files = [f for f in files if not any(f.name.lower().endswith(e) for e in [x for s in cats.values() for x in s])]
            else: cat_files = [f for f in files if any(f.name.lower().endswith(e) for e in exts)]

            if not cat_files:
                st.info("Пусто")
                continue

            # Разбиваем на 2 колонки, новые файлы всегда сверху
            groups = [cat_files[x:x+20] for x in range(0, len(cat_files), 20)]
            cols = st.columns(2 if len(groups) > 1 else [1, 1])

            for g_idx, group in enumerate(groups):
                if g_idx > 1: break 
                with cols[g_idx]:
                    with st.form(key=f"f_{i}_{g_idx}"):
                        h1, h2, h3 = st.columns([0.08, 0.62, 0.3])
                        h1.write("🔘")
                        h2.write("**Файл**")
                        h3.write("**Дата|Кто**")
                        st.markdown("<hr>", unsafe_allow_html=True)

                        selected = []
                        for f in group:
                            r1, r2, r3 = st.columns([0.08, 0.62, 0.3])
                            if r1.checkbox("", key=f"c_{f.name}"): selected.append(f)
                            
                            f_info = get_file_info(f.path)
                            c2 = r2.columns([0.9, 0.1])
                            c2[0].write(f.name)
                            c2[1].link_button("📥", f.download_url)
                            
                            r3.write(f"{f_info[0]}|{f_info[1]}")
                            st.markdown("<hr>", unsafe_allow_html=True)
                        
                        if st.form_submit_button("🗑 Удалить", type="primary"):
                            for sf in selected:
                                repo.delete_file(sf.path, "Del", sf.sha)
                                write_log(st.session_state["user"], "УДАЛИЛ", sf.name)
                            st.rerun()

except Exception as e:
    st.error(f"Ошибка: {e}")
