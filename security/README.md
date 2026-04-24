# Security Stack - DevSecOps Tools
# Semgrep + tfsec + Cosign + Falco + cert-manager

## Overview
```
Code Push → Semgrep (code scan) → tfsec (terraform scan)
         → Trivy (image scan) → Cosign (image sign)
         → Deploy to EKS
         → Falco (runtime monitoring)
         → cert-manager (HTTPS)
```

## Tools

### 1. Semgrep - SAST (in Jenkinsfile Stage 2)
- Scans source code for security bugs
- Runs automatically on every push
- Reports saved as artifacts in Jenkins

### 2. tfsec - Terraform Scanner (in Jenkinsfile Stage 4)
- Scans terraform/ for misconfigurations
- Warns about insecure AWS settings
- Reports saved as artifacts in Jenkins

### 3. Cosign - Image Signing (in Jenkinsfile Stage 7)

#### First time setup (run once on Jenkins EC2):
```bash
chmod +x security/cosign-setup.sh
./security/cosign-setup.sh
```

#### Add to Jenkins credentials:
- cosign-key → Secret file (cosign.key)
- cosign-password → Secret text

### 4. Falco - Runtime Security

#### Deploy:
```bash
kubectl apply -f security/falco/falco.yaml
```

#### View Falco alerts:
```bash
kubectl logs -l app=falco -n falco -f
```

#### What it detects:
- Shell spawned inside container
- Sensitive file reads (/etc/passwd etc.)
- Unexpected network connections
- Privilege escalation attempts
- Package installations inside containers

### 5. cert-manager - Free HTTPS

#### Install cert-manager:
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --for=condition=ready pod -l app=cert-manager -n cert-manager --timeout=120s
```

#### Apply TLS config:
```bash
# Edit cert-manager.yaml first - replace "your-domain.com" with your actual domain
kubectl apply -f security/cert-manager/cert-manager.yaml
```

#### Check certificate status:
```bash
kubectl get certificate -n boutique
kubectl describe certificate boutique-tls -n boutique
```

## Jenkins credentials to add
| ID | Kind | Value |
|---|---|---|
| cosign-password | Secret text | Your cosign key password |
| cosign-key | Secret file | cosign.key file |

## Files
```
security/
├── Jenkinsfile                    → Full pipeline with all security tools
├── cosign-setup.sh                → One-time Cosign key setup
├── falco/
│   └── falco.yaml                 → Runtime security DaemonSet
└── cert-manager/
    └── cert-manager.yaml          → TLS/HTTPS with Let's Encrypt
```

## .gitignore additions needed
```
# Cosign keys - never commit!
cosign.key
cosign.pub
*.key
```
