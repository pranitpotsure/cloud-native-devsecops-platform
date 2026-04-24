# Monitoring Stack - Prometheus + Grafana + Alertmanager

## What each tool does
```
Prometheus    → Collects metrics from all 12 services every 15 seconds
Grafana       → Displays metrics as dashboards (CPU, memory, requests)
Alertmanager  → Sends email when something goes wrong
```

## Setup (run after terraform apply)
```bash
chmod +x monitoring/install.sh
./monitoring/install.sh
```

## Access
| Tool | URL | Login |
|---|---|---|
| Grafana | http://<LoadBalancer-URL> | admin / boutique@123 |
| Prometheus | internal only | - |
| Alertmanager | internal only | - |

## Pre-built Dashboards
- Online Boutique Overview (CPU, Memory, Pods, Network)

## Import free dashboards from grafana.com
```
Go to Grafana → Dashboards → Import → Enter ID:

6417  → Kubernetes Cluster Overview
1860  → Node Exporter Full
6781  → Kubernetes Pods
```

## Alerts configured
| Alert | Trigger | Severity |
|---|---|---|
| PodDown | Pod failed for 1 min | Critical |
| HighCPUUsage | CPU > 80% for 5 mins | Warning |
| HighMemoryUsage | Memory > 85% for 5 mins | Warning |
| PodRestartingTooMuch | Restart in 15 mins | Warning |
| NodeNotReady | Node down for 2 mins | Critical |

## Files
```
monitoring/
├── prometheus/
│   └── prometheus.yaml    → Prometheus + scrape config + alert rules
├── grafana/
│   └── grafana.yaml       → Grafana + datasource + dashboard
├── alertmanager/
│   └── alertmanager.yaml  → Email alerts config
└── install.sh             → One command install
```

## Before deploying - update alertmanager
Open `alertmanager/alertmanager.yaml` and set:
- `smtp_auth_password` → Gmail App Password
  (Gmail → Settings → Security → App Passwords → Generate)
