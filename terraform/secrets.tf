# =============================================================================
# secrets.tf - AWS Secrets Manager
# DevSecOps: No hardcoded secrets anywhere
# =============================================================================

# ── SendGrid Secret ───────────────────────────────────────────────────────────
resource "aws_secretsmanager_secret" "sendgrid" {
  name                    = "${var.project_name}/sendgrid"
  description             = "SendGrid API key for email service"
  recovery_window_in_days = 0  # Allow immediate deletion (for dev)

  tags = {
    Service = "emailservice"
  }
}

resource "aws_secretsmanager_secret_version" "sendgrid" {
  secret_id = aws_secretsmanager_secret.sendgrid.id
  secret_string = jsonencode({
    SENDGRID_API_KEY    = "REPLACE_WITH_YOUR_NEW_SENDGRID_KEY"
    EMAIL_FROM_ADDRESS  = "pranitpotsure72@gmail.com"
    EMAIL_FROM_NAME     = "Online Boutique"
  })
}

# ── Gemini Secret ─────────────────────────────────────────────────────────────
resource "aws_secretsmanager_secret" "gemini" {
  name                    = "${var.project_name}/gemini"
  description             = "Gemini API key for shopping assistant"
  recovery_window_in_days = 0

  tags = {
    Service = "shoppingassistantservice"
  }
}

resource "aws_secretsmanager_secret_version" "gemini" {
  secret_id = aws_secretsmanager_secret.gemini.id
  secret_string = jsonencode({
    GEMINI_API_KEY = "REPLACE_WITH_YOUR_GEMINI_KEY"
  })
}

# ── PostgreSQL Secret ─────────────────────────────────────────────────────────
resource "aws_secretsmanager_secret" "postgres" {
  name                    = "${var.project_name}/postgres"
  description             = "PostgreSQL credentials"
  recovery_window_in_days = 0

  tags = {
    Service = "postgres"
  }
}

resource "aws_secretsmanager_secret_version" "postgres" {
  secret_id = aws_secretsmanager_secret.postgres.id
  secret_string = jsonencode({
    POSTGRES_USER     = "postgres"
    POSTGRES_PASSWORD = "REPLACE_WITH_STRONG_PASSWORD"
    POSTGRES_DB       = "shoppingassistant"
  })
}
