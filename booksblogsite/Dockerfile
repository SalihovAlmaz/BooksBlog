FROM python:3.12-slim AS builder

WORKDIR /tmp
COPY requirements.txt .

RUN pip install psycopg2-binary
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /tmp/wheels -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /tmp/wheels /tmp/wheels
COPY . .

RUN pip install --no-cache-dir /tmp/wheels/*

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]