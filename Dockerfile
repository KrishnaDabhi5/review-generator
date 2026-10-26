FROM python:3.11-slim

# Set UTF-8 encoding to prevent Unicode issues in logging
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway injects PORT at runtime; default to 8000 for local Docker usage
ENV PORT=8000
EXPOSE ${PORT}

CMD python -m uvicorn api.main:app --host 0.0.0.0 --port ${PORT}
