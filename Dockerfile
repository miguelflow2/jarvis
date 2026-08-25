FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn openai python-dotenv
COPY app/cloud_server.py app/cloud_server.py
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.cloud_server:app", "--host", "0.0.0.0", "--port", "8000"]
