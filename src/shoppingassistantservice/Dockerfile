# ShoppingAssistantService Dockerfile - Cloud-Agnostic
#
# CHANGES:
#   - Removed all GCP dependencies (AlloyDB, Secret Manager, Gemini)
#   - Uses PostgreSQL + pgvector + OpenAI instead
#   - DUMMY_MODE=true allows running without any external services
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd -r shoppingassistant && useradd -r -g shoppingassistant shoppingassistant
USER shoppingassistant

# ENV VARS:
#   PORT             - HTTP port (default: 8080)
#   DUMMY_MODE       - "true" to run without LLM/DB (default: true for safety)
#   OPENAI_API_KEY   - Required when DUMMY_MODE=false
#   OPENAI_MODEL     - LLM model (default: gpt-4o-mini)
#   DB_HOST          - PostgreSQL host (default: localhost)
#   DB_PORT          - PostgreSQL port (default: 5432)
#   DB_DATABASE_NAME - Database name (default: shoppingassistant)
#   DB_USER          - Database user (default: postgres)
#   DB_PASSWORD      - Database password
#   DB_TABLE_NAME    - Vector store table (default: products)
ENV PORT=8080 \
    DUMMY_MODE=true

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD wget -qO- http://localhost:8080/_healthz || exit 1

ENTRYPOINT ["python", "shoppingassistantservice.py"]
