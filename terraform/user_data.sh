#!/bin/bash
# ── user_data.sh ──────────────────────────────────────────────────────────
# This script runs automatically on first boot of the EC2 instance.
# It installs Docker, clones the repo, and starts the app.
# Logs are written to /var/log/user-data.log for debugging.
# ──────────────────────────────────────────────────────────────────────────

set -euo pipefail
exec > >(tee /var/log/user-data.log | logger -t user-data) 2>&1

echo "=== TicketDesk bootstrap started ==="

# 1. Update the system package index
yum update -y

# 2. Install Docker
yum install -y docker git

# 3. Start Docker and enable it to start on reboot
systemctl start docker
systemctl enable docker

# 4. Add ec2-user to the docker group so it can run docker without sudo
usermod -aG docker ec2-user

# 5. Install docker-compose v2 plugin
mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64 \
     -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# 6. Clone the ticketdesk repository
git clone https://github.com/Priyanshukainwal0/ticketdesk.git /opt/ticketdesk

# 7. Start the app with docker compose (runs in the background as a daemon)
cd /opt/ticketdesk
docker compose up -d --build

echo "=== TicketDesk bootstrap complete ==="
echo "App running at http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
