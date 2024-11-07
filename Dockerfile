# Используем официальный Python образ
FROM python:3.11

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код бота в контейнер
COPY . /app

# Задаем команду для запуска бота
CMD [ "python", "app.py" ]