# CurrencyService Dockerfile - Cloud-Agnostic
# CHANGES: Removed @google-cloud/profiler. Non-root user added.
FROM node:20-bullseye-slim

WORKDIR /app

COPY package*.json ./
RUN npm install --omit=dev

COPY . .

RUN groupadd -r currencyservice && useradd -r -g currencyservice currencyservice
USER currencyservice

# ENV VARS:
#   PORT             - gRPC port (default: 7000)
#   ENABLE_TRACING   - set to "1" to enable OTel tracing
#   COLLECTOR_SERVICE_ADDR - OTLP collector address
ENV PORT=7000
EXPOSE 7000
ENTRYPOINT ["node", "server.js"]
