FROM python:3.13

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libatlas-base-dev poppler-utils

COPY requirements.txt .

RUN python -m venv /app/venv \
    && /app/venv/bin/pip install --upgrade pip \
    && /app/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY src/ .

CMD ["/app/venv/bin/python", "main.py"]