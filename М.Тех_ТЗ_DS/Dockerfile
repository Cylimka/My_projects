# Используйте официальный образ Python как базовый образ
FROM python:3.8

# Установите рабочую директорию в контейнере
WORKDIR /app

# Копируйте файлы проекта в контейнер
COPY . /app

# Установите необходимые пакеты
RUN pip install --no-cache-dir -r requirements.txt

# Указать порт, который будет использоваться во время выполнения контейнера
EXPOSE 8501

# Команда для запуска приложения
CMD ["streamlit", "run", "main.py"]
