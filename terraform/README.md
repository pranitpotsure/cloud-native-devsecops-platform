# Terraform - AWS Infrastructure
# Online Boutique - Cloud Native DevSecOps Platform

## What this creates
```
AWS (ap-south-1 / Mumbai)
├── VPC (10.0.0.0/16)
│   ├── 2 Public Subnets  → ALB + Jenkins
│   ├── 2 Private Subnets → EKS nodes
│   ├── NAT Gateway
│   └── Internet Gateway
├── EKS Cluster (K8s 1.31)
│   └── Node Group (2x t3.medium)
├── ECR (11 repositories, one per service)
├── Jenkins EC2 (t3.medium)
└── Secrets Manager (SendGrid, Gemini, Postgres)
```

## Cost estimate
| Resource | Cost per hour |
|---|---|
| EKS cluster | ~₹7/hr |
| 2x t3.medium nodes | ~₹5/hr |
| Jenkins t3.medium | ~₹3/hr |
| NAT Gateway | ~₹4/hr |
| **Total** | **~₹20/hr** |

Keep running for 2-3 hours = ₹40-60 total

## Pre-requisites (install before running)

### 1. Install Terraform
```powershell
winget install Hashicorp.Terraform
terraform --version
```

### 2. Install AWS CLI
```powershell
winget install Amazon.AWSCLI
aws --version
```

### 3. Configure AWS credentials
```powershell
aws configure
# Enter:
# AWS Access Key ID: (from AWS Console → IAM → Users → Security credentials)
# AWS Secret Access Key: (same place)
# Default region: ap-south-1
# Default output format: json
```

## Deploy Commands (run when good internet available)

```powershell
# Go to terraform folder
cd C:\Users\prani\DevOps_Project\cloud-native-devsecops-platform\terraform

# Step 1 - Initialize (downloads AWS provider)
terraform init

# Step 2 - See what will be created (no cost yet)
terraform plan

# Step 3 - Create everything (~15 mins)
terraform apply
# Type 'yes' when prompted

# Step 4 - Note the outputs (Jenkins IP, ECR URLs etc.)
terraform output
```

## After deployment

```powershell
# Configure kubectl to use your new EKS cluster
aws eks update-kubeconfig --region ap-south-1 --name boutique-cluster

# Verify nodes are running
kubectl get nodes

# Deploy the app
kubectl apply -f ../k8s/
```

## DESTROY when done (IMPORTANT - saves money!)
```powershell
terraform destroy
# Type 'yes' when prompted
# Takes ~10 mins
```

## Files explained
| File | Purpose |
|---|---|
| `main.tf` | VPC, subnets, routing |
| `eks.tf` | EKS cluster + node group |
| `ecr.tf` | Docker image registries |
| `jenkins.tf` | Jenkins EC2 + auto-install |
| `secrets.tf` | AWS Secrets Manager |
| `variables.tf` | All config in one place |
| `outputs.tf` | Prints URLs after apply |

## Before running - update these values
1. `variables.tf` → `your_ip_cidr` → set to your public IP
2. `secrets.tf` → replace `REPLACE_WITH_*` with real values
