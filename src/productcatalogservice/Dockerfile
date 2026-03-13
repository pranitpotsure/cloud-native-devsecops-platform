# ---------- Build Stage ----------
FROM golang:1.25-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o productcatalogservice


# ---------- Runtime Stage ----------
FROM alpine:3.20

RUN apk add --no-cache ca-certificates

WORKDIR /app
COPY --from=builder /app/productcatalogservice .
COPY products.json .

EXPOSE 3550

ENTRYPOINT ["./productcatalogservice"]