import streamlit as st
import pandas as pd
from github import Github
import os

# --- НАСТРОЙКИ GITHUB ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "arsennurzhanuly/TazaLine" # Проверьте, что имя такое же
FILE_PATH = "database.csv" # Файл, который будет на GitHub

def save_to_github(dataframe):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    # Превращаем таблицу в текст (CSV)
    csv_content = dataframe.to_csv(index=False)
    
    try:
        # Проверяем, существует ли файл, чтобы обновить его
        contents = repo.get_contents(FILE_PATH)
        repo.update_file(contents.path, "Обновление данных через сайт", csv_content, contents.sha)
        st.success("✅ Сохранено в GitHub!")
    except:
        # Если файла еще нет, создаем его
        repo.create_file(FILE_PATH, "Начальное создание базы", csv_content)
        st.success("✅ Файл создан в GitHub!")

# --- АВТОРИЗАЦИЯ ---
def check_password():
    if "auth" not in st.session_state:
        st.session_state["auth"] = False
    if not st.session_state["auth"]:
        st.title("Вход для двоих")
        user = st.text_input("Логин")
        pwd = st.text_input("Пароль", type="password")
        if st.button("Войти"):
            if user == "admin" and pwd == "12345": # Ваши пароли
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Неверно")
        return False
    return True

# --- ОСНОВНОЕ ОКНО ---
if check_password():
    st.title("📊 Общая таблица (Авто-сохранение)")

    # Загружаем актуальные данные из GitHub
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        contents = repo.get_contents(FILE_PATH)
        df = pd.read_csv(contents.download_url)
    except:
        # Если файла нет в репозитории, создаем пустой пример
        df = pd.DataFrame({"Дата": ["2024-01-01"], "Сумма": [0], "Комментарий": ["Начни здесь"]})

    # Редактор таблицы
    st.info("Измените ячейки ниже и нажмите кнопку сохранения")
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    if st.button("💾 СОХРАНИТЬ НАВСЕГДА"):
        with st.spinner('Отправка данных в репозиторий...'):
            save_to_github(edited_df)
