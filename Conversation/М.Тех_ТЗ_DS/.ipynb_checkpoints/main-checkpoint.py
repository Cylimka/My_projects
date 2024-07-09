import streamlit as st
import pandas as pd
import seaborn as sns
sns.set_style('darkgrid')
import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportions_ztest

# Функция для загрузки данных по умолчанию
@st.cache_data(ttl=24*60*60, show_spinner=True)
def load_default_data():
    data_path = 'М.Тех_Данные_к_ТЗ_DS.csv'  # Укажите правильный путь к файлу
    df = pd.read_csv(data_path, encoding='windows-1251')
    df[['count_sick_days', 'age', 'gender']] = df['Количество больничных дней,"Возраст","Пол"'].str.split(',', expand=True)
    df['count_sick_days'] = pd.to_numeric(df['count_sick_days'])
    df['age'] = pd.to_numeric(df['age'])
    df['gender'] = df['gender'].str.replace('"', '').astype('category')
    return df

# Функция для загрузки пользовательского файла
def load_uploaded_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, encoding='windows-1251')
        df[['count_sick_days', 'age', 'gender']] = df['Количество больничных дней,"Возраст","Пол"'].str.split(',', expand=True)
        df['count_sick_days'] = pd.to_numeric(df['count_sick_days'])
        df['age'] = pd.to_numeric(df['age'])
        df['gender'] = df['gender'].str.replace('"', '').astype('category')
        return df
    return None

# Функция для визуализации данных
def plot_data(df, column, title):
    plt.figure(figsize=(10, 6))
    sns.barplot(x=df[column], y=df['more_than_work_days'], errorbar=None)
    plt.title(title)
    plt.xlabel(column)
    plt.ylabel('Доля пропусков')
    st.pyplot(plt)

# Функция z-теста для гендерных различий
def gender_ztest(data, work_days, alpha=0.05):
    data['more_than_2_days'] = data['count_sick_days'] > work_days
    
    count_gender = data.groupby('gender')['more_than_2_days'].sum()
    nobs_gender = data['gender'].value_counts()

    stat_gender, p_value = proportions_ztest(count_gender, nobs_gender)
    st.markdown('Мы провели Z-тест для пропорций и получили такие результаты:')
    st.markdown(f'**p-value: {round(p_value,10)}**')
    if p_value < alpha:
        st.markdown(f'Отвергаем нулевую гипотизу, так как p-value меньше уровня статистической значимости, а это значит что в данных есть различия в долях мужчин и женщин, пропускающих более {work_days} рабочих дней в году')
    else:
        st.markdown(f'Не отвергаем нулевую гипотезу, так как p-value больше уровня статистической значимости, нет статистически значимых различий в долях мужчин и женщин, пропускающих более {work_days} рабочих дней в году')

# Функция z-теста для возрастных различий
def age_ztest(data, age, work_days, alpha=0.05):
    # Фильтрация и подсчет количества мужчин и женщин, пропускающих более work_days рабочих дней
    data['age_group'] = data['age'].apply(lambda x: 'older' if x > 35 else 'younger_or_equal_35')
    
    count_age = data.groupby('age_group')['more_than_2_days'].sum()
    nobs_age = data['age_group'].value_counts()

    # Выполнение z-теста
    stat_age, p_value = proportions_ztest(count_age, nobs_age)

    # Интерпритация результата
    st.markdown('Мы провели Z-тест для пропорций и получили такие результаты:')
    st.markdown(f'**p-value: {round(p_value,10)}**')
    if p_value < alpha:
        st.markdown(f'Отвергаем нулевую гипотизу, так как p-value меньше уровня статистической значимости, Есть статистически значимые различия в долях сотрудников старше {age} лет и младше или равных {age} годам, пропускающих более {work_days} рабочих дней в году')
    else:
        st.markdown(f'Не отвергаем нулевую гипотизу, так как p-value меньше уровня статистической значимости, нет статистически значимых различий в долях сотрудников старше {age} лет и младше или равных {age} годам, пропускающих более {work_days} рабочих дней в году')

# Основная функция приложения Streamlit
def main():
    st.title("Анализ пропусков рабочих дней")

    # Виджет для загрузки файла
    uploaded_file = st.file_uploader("Загрузите CSV файл", type="csv")
    if uploaded_file is not None:
        df = load_uploaded_data(uploaded_file)
    else:
        df = load_default_data()

    # Виджеты для настройки параметров
    work_days = st.sidebar.slider("# Выберите порог больничных дней (work_days)", 1, 7, 2)
    age = st.sidebar.slider("Выберите пороговый возраст (age)", 18, 65, 35)
    alpha = st.sidebar.slider("Выберите уровень значимости(alpha)", 0.01, 0.5, 0.05)

    df['more_than_work_days'] = df['count_sick_days'] > work_days
    df['age_group'] = df['age'].apply(lambda x: 'older_than_' + str(age) if x > age else 'younger_or_equal_' + str(age))

    # Гендерные различия в пропусках'
    st.markdown('# Гендерные различия в пропусках')
    st.markdown(f'Гипотеза: Мужчины пропускают в течение года более {work_days} рабочих дней (work_days) по болезни значимо чаще женщин')
    st.markdown(f'* $H_0$: Нет статистически значимых различий в долях мужчин и женщин, пропускающих более {work_days} рабочих дней в году. ')
    st.markdown(f'* $H_1$: Есть статистически значимые различия в долях мужчин и женщин, пропускающих более {work_days} рабочих дней в году.')
    gender_ztest(df, work_days, alpha=alpha)
    # Визуализация гендерных различий
    plot_data(df, 'gender', 'Гендерные различия в пропусках')

    # Возрастные различия в пропусках
    st.markdown('# Возрастные различия в пропусках')
    st.markdown(f'Гипотеза: Работники старше {age} лет (age) пропускают в течение года более {work_days} рабочих дней (work_days) по болезни значимо чаще своих более молодых коллег.')
    st.markdown(f'* $H_0$: Нет статистически значимых различий в долях сотрудников старше {age} лет и младше или равных {age}годам, пропускающих более {work_days} рабочих дней в году.')
    st.markdown(f'* $H_1$: Есть статистически значимые различия в долях сотрудников старше {age} лет и младше или равных {age} годам, пропускающих более {work_days} рабочих дней в году.')
    age_ztest(df, age, work_days, alpha=alpha)
    # Визуализация возрастных различий
    plot_data(df, 'age_group', 'Возрастные различия в пропусках')

# Запуск приложения
if __name__ == "__main__":
    main()
