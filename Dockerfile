FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace
COPY . /workspace

RUN pip install --no-cache-dir .

EXPOSE 8080

CMD ["python3", ".governance/wbs_server.py", "8080"]
