# EmailService Dockerfile - Cloud-Agnostic
# CHANGES: Removed GCP profiler packages. Non-root user added.
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd -r emailservice && useradd -r -g emailservice emailservice
USER emailservice

# ENV VARS:
#   PORT             - gRPC port (default: 8080)
#   ENABLE_TRACING   - set to "1" to enable OTel tracing
#   COLLECTOR_SERVICE_ADDR - OTLP collector (when tracing enabled)
ENV PORT=8080
EXPOSE 8080
ENTRYPOINT ["python", "email_server.py"]
