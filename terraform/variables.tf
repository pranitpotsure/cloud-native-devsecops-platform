# =============================================================================
# variables.tf - All configurable values in one place
# =============================================================================

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"  # Mumbai - closest to you, cheapest
}

variable "project_name" {
  description = "Project name - used for naming all resources"
  type        = string
  default     = "boutique"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

# ── VPC Config ────────────────────────────────────────────────────────────────
variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones to use"
  type        = list(string)
  default     = ["ap-south-1a", "ap-south-1b"]
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDRs (EKS nodes go here)"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDRs (ALB goes here)"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

# ── EKS Config ────────────────────────────────────────────────────────────────
variable "eks_cluster_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.31"
}

variable "node_instance_type" {
  description = "EC2 instance type for EKS worker nodes"
  type        = string
  default     = "t3.medium"  # 2 vCPU, 4GB RAM - cheapest that works for 11 services
}

variable "node_min_size" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 1
}

variable "node_max_size" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 3
}

variable "node_desired_size" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 2
}

# ── ECR Config ────────────────────────────────────────────────────────────────
variable "ecr_repos" {
  description = "List of ECR repositories to create (one per microservice)"
  type        = list(string)
  default     = [
    "adservice",
    "cartservice",
    "checkoutservice",
    "currencyservice",
    "emailservice",
    "frontend",
    "paymentservice",
    "productcatalogservice",
    "recommendationservice",
    "shippingservice",
    "shoppingassistantservice"
  ]
}

variable "ecr_image_retention_count" {
  description = "Number of images to keep in ECR per repo"
  type        = number
  default     = 5  # Keep only last 5 builds to save storage cost
}

# ── Jenkins EC2 Config ────────────────────────────────────────────────────────
variable "jenkins_instance_type" {
  description = "EC2 instance type for Jenkins"
  type        = string
  default     = "t3.medium"  # 2 vCPU, 4GB RAM
}

variable "your_ip_cidr" {
  description = "Your public IP for SSH access to Jenkins (get from whatismyip.com)"
  type        = string
  default     = "0.0.0.0/0"  # ← CHANGE THIS to your IP like "103.x.x.x/32"
}
