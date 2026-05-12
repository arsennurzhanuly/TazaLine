# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
import streamlit as st
import pandas as pd
import io

# Настройка страницы
st.set_page_config(page_title="Excel Редактор", layout="wide")


# 1. Функция авторизации
def check_password():
    if "auth" not in st.session_state:
        st.session_state["auth"] = False

    if not st.session_state["auth"]:
        st.title("Вход в систему")
        user = st.text_input("Логин")
        pwd = st.text_input("Пароль", type="password")
        if st.button("Войти"):
            if user == "admin" and pwd == "12345":  # Можно заменить на свои данные
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Ошибка: Неверные данные")
        return False
    return True


# 2. Основной интерфейс
if check_password():
    st.sidebar.success("Вы авторизованы")
    if st.sidebar.button("Выйти"):
        st.session_state["auth"] = False
        st.rerun()

    st.title("📂 Загрузка и редактирование файла")

    # Виджет загрузки файла
    uploaded_file = st.file_uploader("Выберите файл Excel или CSV", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        # Определяем формат и читаем
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.subheader("Редактирование данных:")
            # Включаем редактор (динамическое добавление строк включено)
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

            # Создаем кнопки для сохранения/скачивания
            col1, col2 = st.columns(2)

            with col1:
                # Кнопка скачивания обратно в Excel
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    edited_df.to_excel(writer, index=False, sheet_name='Sheet1')

                st.download_button(
                    label="📥 Скачать отредактированный Excel",
                    data=buffer.getvalue(),
                    file_name="edited_data.xlsx",
                    mime="application/vnd.ms-excel"
                )

            with col2:
                if st.button("💾 Сохранить на сервере"):
                    # Здесь код для сохранения в папку проекта или БД
                    edited_df.to_csv("last_saved_data.csv", index=False)
                    st.success("Файл сохранен как 'last_saved_data.csv'!")

        except Exception as e:
            st.error(f"Ошибка при чтении файла: {e}")
    else:
        st.info("Пожалуйста, загрузите файл, чтобы начать работу.")
