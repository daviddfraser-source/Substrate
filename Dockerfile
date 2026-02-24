FROM python:3.11-slim

WORKDIR /workspace
COPY . /workspace

CMD ["python3", "-m", "http.server", "8080"]
