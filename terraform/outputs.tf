# =============================================================================
# outputs.tf - Important values printed after terraform apply
# =============================================================================

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = aws_eks_cluster.main.endpoint
}

output "ecr_registry_url" {
  description = "ECR registry base URL"
  value       = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com"
}

output "ecr_repo_urls" {
  description = "ECR repository URLs for all services"
  value = {
    for repo_name, repo in aws_ecr_repository.services :
    repo_name => repo.repository_url
  }
}

 # output "jenkins_public_ip" {
 # description = "Jenkins EC2 public IP - open http://<this-ip>:8080"
 # value       = aws_instance.jenkins.public_ip
# }

#output "jenkins_ssh_command" {
 # description = "SSH command to connect to Jenkins"
  #value       = "ssh -i your-key.pem ec2-user@${aws_instance.jenkins.public_ip}"
#}

output "kubectl_config_command" {
  description = "Run this to configure kubectl after cluster is ready"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.main.name}"
}

output "next_steps" {
  description = "What to do after terraform apply"
  value       = <<-EOT
    ✅ Infra created! Next steps:

    1. Configure kubectl:
       aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.main.name}

    2. Verify cluster:
       kubectl get nodes

    3. Open Jenkins (LOCAL):
       http://localhost:8090

    4. Deploy app:
       kubectl apply -f k8s/

    5. DESTROY when done (saves money!):
       terraform destroy
  EOT
}

# ── Data source for account ID ────────────────────────────────────────────────
data "aws_caller_identity" "current" {}
