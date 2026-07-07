FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD exec gunicorn --bind :8080 --workers 4 --timeout 0 app:app
