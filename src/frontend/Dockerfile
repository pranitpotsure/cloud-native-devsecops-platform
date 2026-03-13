# Frontend Dockerfile - Cloud-Agnostic
# CHANGES: Removed GCP profiler and metadata deps. Non-root user added.
FROM golang:1.25-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o frontend

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
RUN addgroup -S frontend && adduser -S frontend -G frontend
WORKDIR /app
COPY --from=builder /app/frontend .
COPY templates ./templates
COPY static ./static
USER frontend

# ENV VARS:
#   PORT                          - HTTP port (default: 8080)
#   PRODUCT_CATALOG_SERVICE_ADDR  - e.g. productcatalogservice:3550
#   CURRENCY_SERVICE_ADDR         - e.g. currencyservice:7000
#   CART_SERVICE_ADDR             - e.g. cartservice:7070
#   RECOMMENDATION_SERVICE_ADDR   - e.g. recommendationservice:8080
#   CHECKOUT_SERVICE_ADDR         - e.g. checkoutservice:5050
#   SHIPPING_SERVICE_ADDR         - e.g. shippingservice:50051
#   AD_SERVICE_ADDR               - e.g. adservice:9555
#   SHOPPING_ASSISTANT_SERVICE_ADDR
#   CLUSTER_NAME                  - deployment cluster name (optional)
#   AVAILABILITY_ZONE             - deployment zone (optional, replaces GCP zone)
#   ENABLE_TRACING                - "1" to enable OTel tracing
#   COLLECTOR_SERVICE_ADDR        - OTLP collector
ENV PORT=8080
EXPOSE 8080
ENTRYPOINT ["./frontend"]
