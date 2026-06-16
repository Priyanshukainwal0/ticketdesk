# ── outputs.tf ────────────────────────────────────────────────────────────
# Values printed after `terraform apply` completes.
# Also readable any time with: terraform output
# ──────────────────────────────────────────────────────────────────────────

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance."
  value       = aws_instance.ticketdesk.public_ip
}

output "app_url" {
  description = "Direct URL to the TicketDesk web console."
  value       = "http://${aws_instance.ticketdesk.public_ip}:${var.app_port}"
}

output "api_docs_url" {
  description = "Swagger UI — interactive API documentation."
  value       = "http://${aws_instance.ticketdesk.public_ip}:${var.app_port}/docs"
}

output "ssh_command" {
  description = "SSH command to connect to the instance for debugging."
  value       = "ssh -i ~/.ssh/${var.key_pair_name}.pem ec2-user@${aws_instance.ticketdesk.public_ip}"
}
