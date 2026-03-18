# =============================================================================
# ecr.tf - ECR Repositories for all 11 microservices
# DevSecOps: Image scanning enabled on push
# =============================================================================

resource "aws_ecr_repository" "services" {
  for_each = toset(var.ecr_repos)

  name                 = "${var.project_name}/${each.value}"
  image_tag_mutability = "MUTABLE"

  # DevSecOps: Scan every image on push automatically
  image_scanning_configuration {
    scan_on_push = true
  }

  # DevSecOps: Encrypt images at rest
  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name    = "${var.project_name}/${each.value}"
    Service = each.value
  }
}

# ── ECR Lifecycle Policy - Keep only last 5 images per repo ──────────────────
# Saves storage costs automatically
resource "aws_ecr_lifecycle_policy" "services" {
  for_each   = aws_ecr_repository.services
  repository = each.value.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last ${var.ecr_image_retention_count} images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = var.ecr_image_retention_count
      }
      action = {
        type = "expire"
      }
    }]
  })
}
