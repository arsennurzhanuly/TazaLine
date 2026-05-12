import streamlit as st
from github import Github
import datetime
import base64

# --- НАСТРОЙКИ ---
# Берем токен из секретов Streamlit Cloud
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "arsennurzhanuly/TazaLine" 

# Подключаемся к GitHub
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# --- АВТОРИЗАЦИЯ ---
def check_password():
    if "auth" not in st.session_state:
        st.session_state["auth"] = False
    if not st.session_state["auth"]:
        st.title("🔐 Виртуальная флешка: Вход")
        user = st.text_input("Логин")
        pwd = st.text_input("Пароль", type="password")
        if st.button("Войти"):
            if user == "admin" and pwd == "12345": # Ваши пароли
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Неверный логин или пароль")
        return False
    return True

if check_password():
    st.title("💾 Моя онлайн флешка")
    
    # --- БЛОК 1: ЗАГРУЗКА ФАЙЛА ---
    st.subheader("📤 Загрузить новый файл")
    uploaded_file = st.file_uploader("Выберите любой файл (Excel, Word, Фото и т.д.)")
    
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.name
        
        if st.button(f"Подтвердить загрузку {file_name}"):
            with st.spinner('Копирую на флешку...'):
                try:
                    # Проверяем, нет ли файла с таким именем
                    repo.create_file(file_name, f"Upload {file_name}", file_bytes)
                    st.success(f"Файл {file_name} успешно сохранен!")
                    st.rerun()
                except:
                    st.error("Файл с таким именем уже есть. Переименуйте или удалите старый.")

    st.divider()

    # --- БЛОК 2: СПИСОК ФАЙЛОВ ---
    st.subheader("📁 Содержимое флешки")
    
    # Получаем все файлы из репозитория
    contents = repo.get_contents("")
    
    if len(contents) <= 2: # Если только app.py и requirements.txt
        st.info("Флешка пока пуста (кроме системных файлов)")
    
    for content_file in contents:
        # Пропускаем системные файлы самого сайта
        if content_file.name in ["app.py", "requirements.txt", "README.md", ".gitignore"]:
            continue
            
        # Создаем рамку для каждого файла
        with st.expander(f"📄 {content_file.name}"):
            # Получаем дату последнего изменения
            commit = repo.get_commits(path=content_file.path)[0]
            date_str = commit.commit.author.date.strftime("%d.%m.%Y %H:%M")
            
            st.write(f"Дата загрузки: {date_str}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Кнопка скачивания
                file_data = content_file.decoded_content
                st.download_button(
                    label="📥 Скачать",
                    data=file_data,
                    file_name=content_file.name,
                    mime="application/octet-stream"
                )
            
            with col2:
                # Кнопка удаления
                if st.button("🗑 Удалить", key=content_file.name):
                    repo.delete_file(content_file.path, f"Delete {content_file.name}", content_file.sha)
                    st.warning(f"Файл {content_file.name} удален")
                    st.rerun()
