# ── variables.tf ──────────────────────────────────────────────────────────
# All tunable values live here so main.tf stays readable.
# Override any variable with: terraform apply -var="region=ap-southeast-2"
# ──────────────────────────────────────────────────────────────────────────

variable "region" {
  description = "AWS region to deploy into."
  type        = string
  default     = "ap-southeast-2"   # Sydney — closest to Adelaide
}

variable "instance_type" {
  description = "EC2 instance type. t2.micro is free-tier eligible."
  type        = string
  default     = "t2.micro"
}

variable "key_pair_name" {
  description = <<EOT
Name of an existing EC2 Key Pair for SSH access.
Create one in the AWS Console → EC2 → Key Pairs, then set:
  terraform apply -var="key_pair_name=YOUR_KEY_NAME"
EOT
  type        = string
}

variable "app_port" {
  description = "Port the TicketDesk API listens on inside the container."
  type        = number
  default     = 8000
}
