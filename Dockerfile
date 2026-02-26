FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["gunicorn", "-k", "eventlet", "-w", "1", "-b", "0.0.0.0:10000", "wsgi:app"]