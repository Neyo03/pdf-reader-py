FROM python:3.13

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libatlas-base-dev

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

CMD ["python", "app.py"]