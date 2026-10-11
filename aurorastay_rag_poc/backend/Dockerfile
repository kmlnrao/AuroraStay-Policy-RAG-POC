FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY rag_core.py app.py ./
COPY index/ ./index/
EXPOSE 7860
CMD ["gunicorn", "--workers", "1", "--timeout", "90", "--bind", "0.0.0.0:7860", "app:app"]
