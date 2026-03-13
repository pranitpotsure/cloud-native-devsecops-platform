# =============================================================================
# CartService Dockerfile - Cloud-Agnostic Refactored Version
#
# CHANGES:
#   - Removed AlloyDB and Spanner dependencies (GCP-only)
#   - Removed Google.Cloud.SecretManager references
#   - Multi-stage build retained
#   - Non-root user added for AWS ECS/EKS security best practice
#
# ENV VARS:
#   PORT        - gRPC server port (default: 7070)
#   REDIS_ADDR  - Redis address e.g. redis:6379 or elasticache-endpoint:6379
#                 If unset, falls back to in-memory store (dev only)
# =============================================================================

# ---------- Build Stage ----------
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS builder

WORKDIR /app
COPY src/cartservice.csproj ./
RUN dotnet restore

COPY src/ .
RUN dotnet publish -c Release -o /publish


# ---------- Runtime Stage ----------
FROM mcr.microsoft.com/dotnet/aspnet:10.0

WORKDIR /app
COPY --from=builder /publish .

# Non-root user for AWS ECS/EKS security
RUN groupadd -r cartservice && useradd -r -g cartservice cartservice
USER cartservice

ENV PORT=7070 \
    ASPNETCORE_URLS=http://+:7070

EXPOSE 7070

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD wget -qO- http://localhost:7070/ || exit 1

ENTRYPOINT ["dotnet", "cartservice.dll"]
