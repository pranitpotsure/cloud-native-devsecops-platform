# Logging Stack - Loki + Promtail

## How it works
```
All 12 pods generate logs
        ↓
Promtail (runs on every node) collects logs
        ↓
Ships logs to Loki
        ↓
Grafana queries Loki
        ↓
You search logs in browser
```

## Setup (run after monitoring/install.sh)
```bash
chmod +x logging/install.sh
./logging/install.sh
```

## Useful Log Queries in Grafana → Explore → Loki

### View all boutique service logs
```
{namespace="boutique"}
```

### View logs for specific service
```
{namespace="boutique", service="frontend"}
{namespace="boutique", service="paymentservice"}
{namespace="boutique", service="checkoutservice"}
```

### Search for errors
```
{namespace="boutique"} |= "error"
```

### Search for specific text
```
{namespace="boutique"} |= "payment failed"
{namespace="boutique"} |= "order placed"
{namespace="boutique"} |= "rate_limited"
```

### Count errors per service (last 1 hour)
```
sum by(service) (count_over_time({namespace="boutique"} |= "error" [1h]))
```

## Log-based Alerts configured
| Alert | Trigger |
|---|---|
| PaymentServiceErrors | Any error in paymentservice for 2 mins |
| CheckoutServiceErrors | Any error in checkoutservice for 2 mins |
| HighErrorRate | More than 10 errors/sec across all services |
| EmailServiceFailures | Email sending failures for 5 mins |
| GeminiRateLimited | Shopping assistant rate limited for 5 mins |

## Files
```
logging/
├── loki/
│   ├── loki.yaml              → Loki deployment + config
│   └── loki-alerts.yaml       → Log-based alert rules
├── promtail/
│   └── promtail.yaml          → DaemonSet log collector
├── grafana-loki-datasource.yaml → Adds Loki to Grafana
└── install.sh                 → One command install
```
