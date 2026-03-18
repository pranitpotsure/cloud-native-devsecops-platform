#!/bin/bash
# =============================================================================
# install.sh - Install ArgoCD on EKS
# Run this ONCE after terraform apply
# =============================================================================

set -e

echo "=== Installing ArgoCD on EKS ==="

# ── Step 1: Create ArgoCD namespace ──────────────────────────────────────────
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
echo "✅ Namespace created"

# ── Step 2: Install ArgoCD ────────────────────────────────────────────────────
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
echo "✅ ArgoCD installed"

# ── Step 3: Wait for ArgoCD to be ready ──────────────────────────────────────
echo "⏳ Waiting for ArgoCD pods to be ready (2-3 mins)..."
kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/name=argocd-server \
  -n argocd \
  --timeout=300s
echo "✅ ArgoCD is ready"

# ── Step 4: Expose ArgoCD UI via LoadBalancer ─────────────────────────────────
kubectl patch svc argocd-server -n argocd \
  -p '{"spec": {"type": "LoadBalancer"}}'
echo "✅ ArgoCD UI exposed"

# ── Step 5: Get initial admin password ───────────────────────────────────────
echo ""
echo "=== ArgoCD Login Details ==="
echo "Username: admin"
echo -n "Password: "
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
echo ""

# ── Step 6: Get ArgoCD URL ────────────────────────────────────────────────────
echo ""
echo "⏳ Getting ArgoCD URL (may take 1-2 mins for LoadBalancer)..."
sleep 30
ARGOCD_URL=$(kubectl get svc argocd-server -n argocd \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "✅ ArgoCD URL: https://${ARGOCD_URL}"
echo ""
echo "=== Next Step ==="
echo "Run: kubectl apply -f argocd/apps/app-of-apps.yaml"
