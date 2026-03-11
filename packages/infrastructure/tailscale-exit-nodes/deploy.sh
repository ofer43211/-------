#!/bin/bash
set -euo pipefail

# Deploy a Tailscale exit node on the current machine.
# Usage:
#   ./deploy.sh <authkey> [hostname]
#
# Examples:
#   ./deploy.sh tskey-auth-XXXXX exit-home
#   ./deploy.sh tskey-auth-XXXXX exit-office
#   ./deploy.sh tskey-auth-XXXXX exit-cloud

AUTHKEY="${1:-}"
HOSTNAME="${2:-exit-$(hostname -s)}"

if [ -z "$AUTHKEY" ]; then
    echo "Usage: $0 <TS_AUTHKEY> [hostname]"
    echo ""
    echo "Get an auth key from: https://login.tailscale.com/admin/settings/keys"
    echo "  - Check 'Reusable' if deploying to multiple machines"
    echo "  - Check 'Ephemeral' for temporary nodes"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Create .env file
cat > "$SCRIPT_DIR/.env" <<EOF
TS_AUTHKEY=${AUTHKEY}
TS_HOSTNAME=${HOSTNAME}
EOF

echo "Deploying exit node: ${HOSTNAME}"
echo "---"

# Check prerequisites
if ! command -v docker &>/dev/null; then
    echo "Docker not found. Installing..."
    curl -fsSL https://get.docker.com | sh
fi

# Enable IP forwarding on host (persists across reboots)
echo "Enabling IP forwarding..."
sudo sysctl -w net.ipv4.ip_forward=1 >/dev/null
sudo sysctl -w net.ipv6.conf.all.forwarding=1 >/dev/null

# Persist sysctl settings
if ! grep -q "net.ipv4.ip_forward=1" /etc/sysctl.conf 2>/dev/null; then
    echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf >/dev/null
    echo "net.ipv6.conf.all.forwarding=1" | sudo tee -a /etc/sysctl.conf >/dev/null
fi

# Start the exit node
cd "$SCRIPT_DIR"
docker compose up -d

echo ""
echo "Exit node '${HOSTNAME}' is starting."
echo ""
echo "Next steps:"
echo "  1. Go to https://login.tailscale.com/admin/machines"
echo "  2. Find '${HOSTNAME}' and approve the exit node routes"
echo "  3. On any device: tailscale set --exit-node=${HOSTNAME}"
echo ""
echo "Commands:"
echo "  docker compose logs -f    # view logs"
echo "  docker compose down       # stop"
echo "  docker compose restart    # restart"
