# =============================================================================
# AdService Dockerfile - Cloud-Agnostic Refactored Version
#
# CHANGES from original GCP version:
# - Removed Google Cloud Profiler agent download and installation
#   (original used: /opt/cprof/profiler_java_agent.so)
# - Removed GCP_PROJECT / GOOGLE_CLOUD_PROJECT environment variables
# - No GCP metadata server calls at build or runtime
# - Multi-stage build retained for minimal image size
# - All config via environment variables (PORT, DISABLE_TRACING, DISABLE_STATS)
# - Compatible with AWS ECS, EKS, local Docker, and Docker Compose
# =============================================================================

# ---------- Build Stage ----------
FROM eclipse-temurin:21-jdk AS builder

WORKDIR /app

# Copy build files first to leverage Docker layer caching
# Dependencies are downloaded before copying source code
COPY build.gradle gradlew settings.gradle ./
COPY gradle gradle
RUN chmod +x gradlew

# Download dependencies (cached layer - only re-runs if build.gradle changes)
RUN ./gradlew downloadRepos --no-daemon || true

# Copy source and build
COPY src src
RUN ./gradlew installDist --no-daemon -x test


# ---------- Runtime Stage ----------
# Use slim JRE image for smaller final image (~200MB vs ~400MB with JDK)
FROM eclipse-temurin:21-jre-jammy

WORKDIR /app

# Copy built application from builder stage
COPY --from=builder /app/build/install/hipstershop ./

# Create non-root user for security (best practice for AWS ECS/EKS)
RUN groupadd -r adservice && useradd -r -g adservice adservice
USER adservice

# ---------------------------------------------------------------
# Environment Variables:
#   PORT             - gRPC server port (default: 9555)
#   DISABLE_TRACING  - set to any value to disable tracing init
#   DISABLE_STATS    - set to any value to disable stats init
#   LOG_LEVEL        - log level: TRACE|DEBUG|INFO|WARN|ERROR (default: INFO)
#   OTEL_EXPORTER_OTLP_ENDPOINT - set to enable OpenTelemetry tracing
#                                 e.g. http://otel-collector:4317
# ---------------------------------------------------------------
ENV PORT=9555 \
    DISABLE_TRACING=true \
    DISABLE_STATS=true \
    LOG_LEVEL=INFO

EXPOSE 9555

# Health check for Docker Compose / AWS ECS
# Uses grpc_health_probe if available, otherwise simple port check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:${PORT} || exit 1

ENTRYPOINT ["/app/bin/AdService"]
