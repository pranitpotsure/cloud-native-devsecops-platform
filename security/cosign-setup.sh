#!/bin/bash
# =============================================================================
# cosign-setup.sh - Setup Cosign image signing
# Run ONCE on Jenkins EC2 to generate signing keys
# =============================================================================

set -e

echo "=== Setting up Cosign Image Signing ==="

# ── Install Cosign ────────────────────────────────────────────────────────────
echo "📦 Installing Cosign..."
curl -O -L "https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64"
mv cosign-linux-amd64 /usr/local/bin/cosign
chmod +x /usr/local/bin/cosign
echo "✅ Cosign installed: $(cosign version)"

# ── Generate key pair ─────────────────────────────────────────────────────────
echo ""
echo "🔑 Generating Cosign key pair..."
echo "Enter a strong password when prompted (save it in Jenkins credentials as 'cosign-password')"
cosign generate-key-pair --output-key-prefix cosign

echo ""
echo "=== Keys generated ==="
echo "cosign.key  → PRIVATE KEY (never share, add to Jenkins credentials)"
echo "cosign.pub  → PUBLIC KEY  (safe to share, add to K8s for verification)"

# ── Add public key to K8s for verification ────────────────────────────────────
echo ""
echo "📋 Adding public key to K8s..."
kubectl create secret generic cosign-public-key \
  --from-file=cosign.pub \
  --namespace=boutique \
  --dry-run=client -o yaml | kubectl apply -f -

echo ""
echo "=== Next Steps ==="
echo "1. Add cosign.key content to Jenkins credentials:"
echo "   Jenkins → Manage Jenkins → Credentials → Add"
echo "   Kind: Secret file"
echo "   ID: cosign-key"
echo ""
echo "2. Add cosign password to Jenkins credentials:"
echo "   Kind: Secret text"
echo "   ID: cosign-password"
echo ""
echo "3. Delete local key files (stored in Jenkins now):"
echo "   rm cosign.key cosign.pub"
