#!/bin/bash
# =============================================================================
# install.sh - Install full monitoring stack on EKS
# Prometheus + Grafana + Alertmanager
# Run after: terraform apply + kubectl apply -f k8s/
# =============================================================================

set -e

echo "=== Installing Monitoring Stack ==="

# ── Step 1: Apply all monitoring manifests ────────────────────────────────────
echo "📊 Deploying Prometheus..."
kubectl apply -f monitoring/prometheus/prometheus.yaml

echo "📈 Deploying Grafana..."
kubectl apply -f monitoring/grafana/grafana.yaml

echo "🚨 Deploying Alertmanager..."
kubectl apply -f monitoring/alertmanager/alertmanager.yaml

# ── Step 2: Wait for pods to be ready ─────────────────────────────────────────
echo "⏳ Waiting for monitoring pods to be ready..."
kubectl wait --for=condition=ready pod \
  -l app=prometheus -n monitoring --timeout=120s
kubectl wait --for=condition=ready pod \
  -l app=grafana -n monitoring --timeout=120s
echo "✅ All monitoring pods ready"

# ── Step 3: Get Grafana URL ───────────────────────────────────────────────────
echo "⏳ Getting Grafana URL..."
sleep 30
GRAFANA_URL=$(kubectl get svc grafana -n monitoring \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

echo ""
echo "=== Monitoring Stack Ready! ==="
echo "📊 Prometheus : http://prometheus:9090 (internal)"
echo "📈 Grafana    : http://${GRAFANA_URL}"
echo "   Username   : admin"
echo "   Password   : boutique@123"
echo ""
echo "=== Pre-built Dashboards ==="
echo "→ Online Boutique Overview (CPU, Memory, Pods, Network)"
echo ""
echo "=== Import more dashboards from grafana.com ==="
echo "→ K8s Cluster: ID 6417"
echo "→ Node Exporter: ID 1860"
echo "→ K8s Pods: ID 6781"
