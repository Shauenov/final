FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git curl && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

RUN addgroup --system app && adduser --system app

USER app
EXPOSE 8000
COPY --chown=app:app ./ /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
