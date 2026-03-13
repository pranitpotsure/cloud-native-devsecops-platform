# Kubernetes Manifests - Online Boutique
# Cloud-Agnostic | DevSecOps Ready

## Directory Structure
```
k8s/
├── namespace/
│   └── namespace.yaml          # boutique namespace
├── secrets/
│   ├── secrets.yaml            # API keys (SendGrid, Gemini, DB)
│   └── configmap.yaml          # Non-sensitive env vars
├── infrastructure/
│   └── infrastructure.yaml     # Redis + PostgreSQL
├── services/
│   └── services.yaml           # All 12 microservices
└── network/
    ├── ingress.yaml            # Expose frontend
    └── networkpolicy.yaml      # Zero-trust networking (DevSecOps)
```

## Deploy Order (IMPORTANT)
```bash
# 1. Create namespace first
kubectl apply -f namespace/namespace.yaml

# 2. Create secrets and config
kubectl apply -f secrets/secrets.yaml
kubectl apply -f secrets/configmap.yaml

# 3. Start infrastructure
kubectl apply -f infrastructure/infrastructure.yaml

# 4. Wait for infrastructure to be ready
kubectl wait --for=condition=ready pod -l app=redis -n boutique --timeout=60s
kubectl wait --for=condition=ready pod -l app=postgres -n boutique --timeout=60s

# 5. Deploy all services
kubectl apply -f services/services.yaml

# 6. Apply networking
kubectl apply -f network/networkpolicy.yaml
kubectl apply -f network/ingress.yaml
```

## Verify Everything is Running
```bash
kubectl get pods -n boutique
kubectl get services -n boutique
kubectl get ingress -n boutique
```

## DevSecOps Features
- ✅ Non-root containers (runAsNonRoot: true)
- ✅ Resource limits on every pod
- ✅ Health probes (readiness + liveness)
- ✅ Secrets separate from config
- ✅ NetworkPolicies (zero-trust)
- ✅ Only frontend exposed via Ingress

## Before Deploying to AWS EKS
Replace all `your-dockerhub/` image references with your actual
DockerHub username or ECR registry URL:
```bash
# Example
your-dockerhub/frontend:latest
→ 123456789.dkr.ecr.ap-south-1.amazonaws.com/frontend:latest
```
