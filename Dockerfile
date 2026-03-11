FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml .
COPY qq_bot/ qq_bot/

RUN pip install --no-cache-dir .

CMD ["python", "-m", "qq_bot.main"]
