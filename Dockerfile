FROM python:3.11-slim

# Создаём директорию и даём права
RUN mkdir -p /app && chmod 755 /app
WORKDIR /app

# Копируем зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Даём права на файлы (важно!)
RUN chmod +x main.py kinopoisk_client.py && \
    chown -R root:root /app && \
    chmod -R 755 /app

EXPOSE 8000

CMD ["python", "main.py"]