#!/bin/bash

# Create SSL directory
mkdir -p ssl

# Generate self-signed certificate for localhost
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=localhost"

echo "✅ Self-signed SSL certificates generated in ./ssl/"
echo "📁 Files created:"
echo "   - ssl/cert.pem (certificate)"
echo "   - ssl/key.pem (private key)"
echo ""
echo "🚀 Now you can run: docker-compose up -d"
echo "🌐 Access your app at: https://localhost" 