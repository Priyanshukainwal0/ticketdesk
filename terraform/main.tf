# ── main.tf ───────────────────────────────────────────────────────────────
#
# Terraform configuration for TicketDesk on AWS (Phase 4).
#
# What this creates:
#   - 1 × EC2 t2.micro instance (free-tier eligible)
#   - 1 × Security group (ports 22, 8000, 443 open; all egress allowed)
#   - User data script that installs Docker and starts the app on boot
#
# Usage:
#   cd terraform/
#   terraform init
#   terraform plan   -var="key_pair_name=YOUR_KEY"
#   terraform apply  -var="key_pair_name=YOUR_KEY"
#   terraform destroy -var="key_pair_name=YOUR_KEY"   # tear down to avoid charges
# ──────────────────────────────────────────────────────────────────────────


# ── Terraform & provider requirements ─────────────────────────────────────

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}


# ── AWS provider ───────────────────────────────────────────────────────────
# Credentials are read from environment variables (never hard-code keys):
#   $env:AWS_ACCESS_KEY_ID     = "AKIA..."
#   $env:AWS_SECRET_ACCESS_KEY = "..."
# Or run `aws configure` if you have the AWS CLI installed.

provider "aws" {
  region = var.region
}


# ── Data: look up the latest Amazon Linux 2023 AMI ─────────────────────────
# Using a data source means we always get the current AMI for our region
# without hard-coding an AMI ID that may become outdated.

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}


# ── Security group ─────────────────────────────────────────────────────────
# Controls inbound and outbound traffic for the EC2 instance.

resource "aws_security_group" "ticketdesk" {
  name        = "ticketdesk-sg"
  description = "Allow SSH, HTTP app traffic, and all outbound for TicketDesk."

  # SSH — for manual debugging / emergency access
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   # restrict to your IP in production
  }

  # TicketDesk API
  ingress {
    description = "TicketDesk API"
    from_port   = var.app_port
    to_port     = var.app_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # All outbound traffic allowed — needed for yum updates, docker pulls, git clone
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"   # all protocols
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "ticketdesk-sg"
    Project = "ticketdesk"
  }
}


# ── EC2 instance ───────────────────────────────────────────────────────────

resource "aws_instance" "ticketdesk" {
  # Amazon Linux 2023 AMI (resolved dynamically above)
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  # Key pair for SSH access (must already exist in AWS)
  key_name = var.key_pair_name

  # Attach the security group defined above
  vpc_security_group_ids = [aws_security_group.ticketdesk.id]

  # Assign a public IP so the app is reachable from the internet
  associate_public_ip_address = true

  # Bootstrap script — installs Docker and starts the app
  user_data = file("${path.module}/user_data.sh")

  # Give the instance extra time to complete Docker build on first boot
  # (t2.micro is slow; the app is usually ready within 3-4 minutes)

  tags = {
    Name    = "ticketdesk"
    Project = "ticketdesk"
    Phase   = "4-terraform"
  }
}
