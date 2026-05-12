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
    st.error("Настройте GITHUB_TOKEN в Secrets (раздел Settings в Streamlit Cloud)!")
    st.stop()

# --- АВТОРИЗАЦИЯ ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.title("🔐 Вход в хранилище")
    u = st.text_input("Логин")
    p = st.text_input("Пароль", type="password")
    if st.button("Войти"):
        if u == "admin" and p == "12345":
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Неверно")
    st.stop()

# --- ОСНОВНОЙ ИНТЕРФЕЙС ---
st.title("💾 Виртуальная флешка")

# Блок загрузки (Множественный)
st.subheader("📤 Загрузка файлов")
uploaded_files = st.file_uploader("Выберите один или несколько файлов", accept_multiple_files=True)

if uploaded_files:
    if st.button(f"Загрузить все файлы ({len(uploaded_files)} шт.)"):
        for uploaded_file in uploaded_files:
            file_bytes = uploaded_file.read()
            name = uploaded_file.name
            try:
                # Пытаемся создать файл
                repo.create_file(name, f"Add {name}", file_bytes)
                st.success(f"✅ {name} сохранен")
            except Exception as e:
                # Если файл уже существует, GitHub вернет ошибку 422
                if "422" in str(e):
                    st.error(f"❌ {name} уже есть на флешке")
                else:
                    st.error(f"❌ Ошибка {name}: {e}")
        st.info("Обновите страницу, чтобы увидеть новые файлы в списке")

st.divider()

# Блок списка файлов (Сетка)
st.subheader("📁 Файлы в облаке")

try:
    all_contents = repo.get_contents("")
    # Убираем служебные файлы сайта, чтобы не мешались на флешке
    files = [f for f in all_contents if f.name not in ["app.py", "requirements.txt", "README.md", ".gitignore", "database.csv"]]
    
    if not files:
        st.info("Флешка пуста")
    else:
        # Создаем сетку (3 колонки)
        cols = st.columns(3)
        for idx, f in enumerate(files):
            with cols[idx % 3]:
                # Заголовок файла (обрезаем если слишком длинный)
                display_name = f.name if len(f.name) < 20 else f.name[:17] + "..."
                st.markdown(f"{display_name}")
                
                # Дата загрузки из GitHub
                try:
                    commit = repo.get_commits(path=f.path)[0]
                    # Время в GitHub по UTC, добавляем 5 часов для КЗ
                    dt = commit.commit.author.date + datetime.timedelta(hours=5)
                    st.caption(f"📅 {dt.strftime('%d.%m %H:%M')}")
                except:
                    st.caption("📅 Дата не определена")
                
                # Кнопки действий
                btn_cols = st.columns(2)
                with btn_cols[0]:
                    st.download_button("📥", f.decoded_content, f.name, key=f"dl_{f.name}", help="Скачать")
                with btn_cols[1]:
                    if st.button("🗑", key=f"del_{f.name}", help="Удалить"):
                        repo.delete_file(f.path, f"Del {f.name}", f.sha)
                        st.rerun()
                st.markdown("---")
except Exception as e:
    st.error(f"Ошибка при получении списка: {e}")
