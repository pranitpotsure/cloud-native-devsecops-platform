#!/bin/bash
# =============================================================================
# install.sh - Install Loki + Promtail logging stack
# Run AFTER monitoring/install.sh
# =============================================================================

set -e

echo "=== Installing Logging Stack (Loki + Promtail) ==="

# ── Deploy Loki ───────────────────────────────────────────────────────────────
echo "📋 Deploying Loki..."
kubectl apply -f logging/loki/loki.yaml
kubectl apply -f logging/loki/loki-alerts.yaml

# ── Deploy Promtail on all nodes ──────────────────────────────────────────────
echo "📋 Deploying Promtail (log collector)..."
kubectl apply -f logging/promtail/promtail.yaml

# ── Update Grafana with Loki datasource ───────────────────────────────────────
echo "📊 Adding Loki datasource to Grafana..."
kubectl apply -f logging/grafana-loki-datasource.yaml
kubectl rollout restart deployment/grafana -n monitoring

# ── Wait for pods ─────────────────────────────────────────────────────────────
echo "⏳ Waiting for Loki to be ready..."
kubectl wait --for=condition=ready pod \
  -l app=loki -n monitoring --timeout=120s
echo "✅ Loki ready"

echo ""
echo "=== Logging Stack Ready! ==="
echo ""
echo "📋 How to view logs in Grafana:"
echo "   1. Open Grafana URL"
echo "   2. Go to Explore (compass icon)"
echo "   3. Select datasource: Loki"
echo "   4. Use these queries:"
echo ""
echo "   All boutique logs:"
echo '   {namespace="boutique"}'
echo ""
echo "   Frontend errors only:"
echo '   {namespace="boutique", service="frontend"} |= "error"'
echo ""
echo "   Payment failures:"
echo '   {namespace="boutique", service="paymentservice"} |= "error"'
echo ""
echo "   All errors across all services:"
echo '   {namespace="boutique"} |= "error"'
