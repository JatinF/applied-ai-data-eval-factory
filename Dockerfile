FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY configs ./configs
COPY data ./data
COPY reports ./reports

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["data-eval", "serve", "--host", "0.0.0.0", "--port", "8000"]
