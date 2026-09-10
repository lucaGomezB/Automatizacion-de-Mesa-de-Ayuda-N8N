#!/usr/bin/env bash
# generate-certs.sh — Generate self-signed TLS certificate for local development
#
# Usage:
#   bash openssl/generate-certs.sh
#
# Output:
#   openssl/mesa.crt — Self-signed X.509 certificate (365 days, RSA 2048-bit, SHA-256)
#   openssl/mesa.key — Private key (RSA 2048-bit)
#
# This script is idempotent: re-running overwrites existing certificates.
# The certificate includes SANs for localhost, 127.0.0.1, and mesa.local.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR"

mkdir -p "$OUTPUT_DIR"

# Build an OpenSSL config file with SANs for maximum compatibility
# (older OpenSSL versions do not support the -addext flag)
CONFIG_FILE="$(mktemp)"
cat > "$CONFIG_FILE" << 'OPENSSL_CONFIG'
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = localhost

[v3_req]
subjectAltName = @alt_names
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth

[alt_names]
DNS.1 = localhost
DNS.2 = mesa.local
IP.1 = 127.0.0.1
OPENSSL_CONFIG

echo "Generating self-signed TLS certificate (RSA 2048-bit, valid for 365 days)..."

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout "$OUTPUT_DIR/mesa.key" \
  -out "$OUTPUT_DIR/mesa.crt" \
  -config "$CONFIG_FILE" \
  -extensions v3_req

rm -f "$CONFIG_FILE"

# Restrict key file permissions (best effort — may not apply on all filesystems)
chmod 600 "$OUTPUT_DIR/mesa.key" 2>/dev/null || true
chmod 644 "$OUTPUT_DIR/mesa.crt" 2>/dev/null || true

echo ""
echo "Certificate generated successfully."
echo "  Certificate : $OUTPUT_DIR/mesa.crt"
echo "  Private key : $OUTPUT_DIR/mesa.key"
echo ""
echo "You can verify with:"
echo "  openssl x509 -in $OUTPUT_DIR/mesa.crt -text -noout | head -20"
