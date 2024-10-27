# Используйте официальный образ Python нужной версии в качестве базового
FROM python

# Установите рабочую директорию в контейнере
WORKDIR /main

# Скопируйте файл requirements.txt в контейнер
COPY requirements.txt .

# Установите зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Скопируйте остальные файлы проекта в контейнер
COPY . .

# Команда для запуска приложения
CMD ["python", "main.py"]
