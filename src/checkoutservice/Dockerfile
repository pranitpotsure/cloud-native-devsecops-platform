# CheckoutService Dockerfile - Cloud-Agnostic
# CHANGES: Removed GCP profiler. Non-root user added.
FROM golang:1.25-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o checkoutservice

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
RUN addgroup -S checkoutservice && adduser -S checkoutservice -G checkoutservice
WORKDIR /app
COPY --from=builder /app/checkoutservice .
USER checkoutservice

# ENV VARS:
#   PORT                        - gRPC port (default: 5050)
#   SHIPPING_SERVICE_ADDR       - e.g. shippingservice:50051
#   PRODUCT_CATALOG_SERVICE_ADDR
#   CART_SERVICE_ADDR
#   CURRENCY_SERVICE_ADDR
#   EMAIL_SERVICE_ADDR
#   PAYMENT_SERVICE_ADDR
#   ENABLE_TRACING              - set to "1" to enable OTel tracing
#   COLLECTOR_SERVICE_ADDR      - OTLP collector (when tracing enabled)
ENV PORT=5050
EXPOSE 5050
ENTRYPOINT ["./checkoutservice"]
