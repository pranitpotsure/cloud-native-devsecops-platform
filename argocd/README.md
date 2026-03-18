# ArgoCD - GitOps for Online Boutique
# Auto sync for dev | Manual sync for prod

## How it works
```
Developer pushes code
        ↓
Jenkins builds & pushes image to ECR
        ↓
Jenkins updates image tag in k8s/services/services.yaml
        ↓
Jenkins pushes updated manifest to GitHub
        ↓
ArgoCD detects Git change (polls every 3 mins)
        ↓
ArgoCD auto-deploys to EKS (dev)
        ↓
App updated with zero downtime!
```

## Setup Commands (run after terraform apply)

### 1. Install ArgoCD
```bash
chmod +x argocd/install/install.sh
./argocd/install/install.sh
```

### 2. Install ArgoCD CLI
```bash
# On EC2/Linux
curl -sSL -o /usr/local/bin/argocd \
  https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x /usr/local/bin/argocd

# On Windows
winget install ArgoProj.ArgoCD
```

### 3. Login to ArgoCD
```bash
# Get URL
ARGOCD_URL=$(kubectl get svc argocd-server -n argocd -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

# Get password
ARGOCD_PASS=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)

# Login
argocd login $ARGOCD_URL --username admin --password $ARGOCD_PASS --insecure
```

### 4. Create ArgoCD projects
```bash
kubectl apply -f argocd/apps/project.yaml
```

### 5. Deploy app-of-apps (manages everything)
```bash
kubectl apply -f argocd/apps/app-of-apps.yaml
```

### 6. Verify
```bash
# Check all apps
argocd app list

# Check sync status
argocd app get boutique-dev

# Watch sync in real time
argocd app wait boutique-dev --sync
```

## Manual prod deploy (when ready)
```bash
# Sync production manually
argocd app sync boutique-prod

# Watch rollout
kubectl rollout status deployment/frontend -n boutique-prod
```

## Useful ArgoCD commands
```bash
# List all apps
argocd app list

# Get app details
argocd app get boutique-dev

# Force sync
argocd app sync boutique-dev --force

# Rollback to previous version
argocd app rollback boutique-dev 1

# Delete app (keeps K8s resources)
argocd app delete boutique-dev --cascade=false
```

## Files explained
| File | Purpose |
|---|---|
| `install/install.sh` | Installs ArgoCD on EKS |
| `apps/app-of-apps.yaml` | Master app - manages all other apps |
| `apps/boutique-dev.yaml` | Dev app - auto sync |
| `apps/boutique-prod.yaml` | Prod app - manual sync |
| `apps/project.yaml` | RBAC - restricts prod access |
| `Jenkinsfile.aws` | AWS pipeline that triggers ArgoCD |
