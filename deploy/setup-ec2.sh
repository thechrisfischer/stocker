#!/bin/bash
# EC2 instance initial setup script
# Run as root on a fresh Ubuntu 22.04+ instance

set -euo pipefail

echo "=== Installing system dependencies ==="
apt-get update
apt-get install -y python3 python3-venv python3-pip sqlite3 nodejs npm

echo "=== Installing Caddy ==="
apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt-get update
apt-get install -y caddy

echo "=== Creating stocker user ==="
useradd --system --create-home --shell /bin/bash stocker || true

echo "=== Setting up application directory ==="
mkdir -p /opt/stocker/data
chown -R stocker:stocker /opt/stocker

echo "=== Cloning and setting up application ==="
su - stocker -c "
    cd /opt/stocker
    git clone https://github.com/thechrisfischer/stocker.git .

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

    cd static
    npm install
    npm run build:production
    cd ..

    # Generate a real secret key
    SECRET_KEY=\$(python3 -c 'import os; print(os.urandom(32).hex())')
    echo \"SECRET_KEY=\$SECRET_KEY\" > /opt/stocker/.env
    echo \"DATABASE_URL=sqlite:////opt/stocker/data/stocker.db\" >> /opt/stocker/.env
    echo \"FLASK_DEBUG=false\" >> /opt/stocker/.env

    # Create database
    export SECRET_KEY=\$SECRET_KEY
    export DATABASE_URL=sqlite:////opt/stocker/data/stocker.db
    flask create-db
"

echo "=== Installing systemd service ==="
cp /opt/stocker/deploy/stocker.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable stocker
systemctl start stocker

echo "=== Configuring Caddy ==="
cp /opt/stocker/deploy/Caddyfile /etc/caddy/Caddyfile
systemctl restart caddy

echo "=== Setting up backup cron ==="
chmod +x /opt/stocker/deploy/backup.sh
echo "0 2 * * * stocker /opt/stocker/deploy/backup.sh" > /etc/cron.d/stocker-backup

echo "=== Setup complete ==="
echo "Edit /etc/caddy/Caddyfile to set your domain name"
echo "Edit /etc/systemd/system/stocker.service to set SECRET_KEY"
echo "Then: systemctl restart stocker && systemctl restart caddy"
