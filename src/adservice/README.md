# AdService — Cloud-Agnostic Refactored Version

## What Changed from the Original GCP Version

### 1. Removed GCP Dependencies

| Original (GCP) | Refactored (Cloud-Agnostic) |
|---|---|
| GCP Cloud Profiler JVM agent (`-agentpath:/opt/cprof/...`) | Removed entirely. Use AWS CodeGuru Profiler optionally. |
| Stackdriver JSON log keys (`logging.googleapis.com/trace`, etc.) | Plain JSON stdout logs — compatible with any log aggregator |
| GCP-specific tracing exporter (Stackdriver Trace) | Stub with env-var guard; wire OpenTelemetry OTLP for any backend |
| GCP Metadata Server calls | None — all config via environment variables |
| `GOOGLE_CLOUD_PROJECT` / `GCP_PROJECT` env vars | Not required |

### 2. Files Changed

| File | Changes |
|---|---|
| `src/main/java/hipstershop/AdService.java` | Cleaned `initStats()` and `initTracing()` — no GCP calls; added clear comments for enabling OTel |
| `src/main/resources/log4j2.xml` | Removed all `logging.googleapis.com/*` keys; clean JSON stdout; `LOG_LEVEL` env var support |
| `build.gradle` | Removed commented GCP Profiler JVM agent flags; added OTel deps as commented-out optional section |
| `Dockerfile` | Removed GCP Profiler download; added non-root user; added ENV defaults; improved layer caching |
| `docker-compose.yml` | **New file** — for local development without any GCP infrastructure |

### 3. Business Logic — Untouched

All ad serving logic is preserved exactly:
- `getAds()` gRPC handler
- `getAdsByCategory()` category lookup
- `getRandomAds()` fallback
- `createAdsMap()` with all 7 products and categories

---

## Running Locally

```bash
# Build and start
docker compose up --build

# Test with grpcurl
grpcurl -plaintext -d '{"context_keys": ["clothing"]}' \
  localhost:9555 hipstershop.AdService/GetAds

# View logs
docker compose logs -f adservice

# Stop
docker compose down
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `PORT` | `9555` | gRPC server port |
| `DISABLE_TRACING` | `true` | Set to disable tracing init |
| `DISABLE_STATS` | `true` | Set to disable stats init |
| `LOG_LEVEL` | `INFO` | Log level: TRACE, DEBUG, INFO, WARN, ERROR |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | _(unset)_ | Set to enable OpenTelemetry tracing |
| `OTEL_SERVICE_NAME` | _(unset)_ | Service name for OTel traces |

---

## Deploying to AWS

### AWS ECS (Fargate)
1. Push image to ECR: `docker tag adservice:local <account>.dkr.ecr.<region>.amazonaws.com/adservice:latest`
2. Create ECS Task Definition with:
   - Port mapping: `9555/tcp`
   - Log driver: `awslogs` (CloudWatch Logs — reads stdout automatically)
   - Environment variables from the table above

### AWS EKS (Kubernetes)
```yaml
env:
  - name: PORT
    value: "9555"
  - name: DISABLE_TRACING
    value: "true"
  - name: LOG_LEVEL
    value: "INFO"
```

### Optional: Enable Tracing on AWS
1. Deploy [AWS Distro for OpenTelemetry (ADOT) Collector](https://aws-otel.github.io/)
2. Set in your task/pod:
   ```
   DISABLE_TRACING=false
   OTEL_EXPORTER_OTLP_ENDPOINT=http://adot-collector:4317
   OTEL_SERVICE_NAME=adservice
   ```
3. Uncomment OTel dependencies in `build.gradle`

---

## Optional: Enable AWS CodeGuru Profiler
Uncomment in `build.gradle`:
```groovy
defaultJvmOpts = ["-javaagent:/opt/codeguru-profiler/codeguru-profiler-java-agent-standalone.jar"]
```
And add the agent JAR to your Docker image.
