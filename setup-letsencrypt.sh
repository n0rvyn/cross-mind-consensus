#!/bin/bash

# Setup Let's Encrypt SSL certificates for production
# Usage: ./setup-letsencrypt.sh your-domain.com your-email@example.com

DOMAIN=${1:-localhost}
EMAIL=${2:-admin@example.com}

if [ "$DOMAIN" == "localhost" ]; then
    echo "⚠️  Warning: Using localhost domain. For production, run:"
    echo "   ./setup-letsencrypt.sh your-domain.com your-email@example.com"
    echo ""
fi

echo "🔧 Setting up Let's Encrypt SSL for domain: $DOMAIN"
echo "📧 Using email: $EMAIL"

# Create SSL directory
mkdir -p ssl

# Create docker-compose override for Certbot
cat > docker-compose.certbot.yml << EOF
version: '3.8'

services:
  certbot:
    image: certbot/certbot
    container_name: consensus-certbot
    volumes:
      - ./ssl:/etc/letsencrypt
      - ./certbot-webroot:/var/www/certbot
    command: certonly --webroot --webroot-path=/var/www/certbot --email $EMAIL --agree-tos --no-eff-email -d $DOMAIN

  nginx:
    volumes:
      - ./certbot-webroot:/var/www/certbot:ro
      - ./ssl/live/$DOMAIN/fullchain.pem:/etc/nginx/ssl/cert.pem:ro
      - ./ssl/live/$DOMAIN/privkey.pem:/etc/nginx/ssl/key.pem:ro
EOF

# Create nginx config with Let's Encrypt support
cat > nginx-letsencrypt.conf << EOF
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Upstream servers
    upstream api_backend {
        server api:8000;
    }

    upstream dashboard_backend {
        server dashboard:8501;
    }

    # HTTP server for Let's Encrypt challenges and redirect
    server {
        listen 80;
        server_name $DOMAIN;

        # Let's Encrypt challenge
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        # Redirect all other HTTP traffic to HTTPS
        location / {
            return 301 https://\$server_name\$request_uri;
        }
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name $DOMAIN;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        
        # SSL Security
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # API endpoints
        location /api/ {
            proxy_pass http://api_backend/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Dashboard
        location / {
            proxy_pass http://dashboard_backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            
            # WebSocket support for Streamlit
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
EOF

echo "✅ Created Let's Encrypt configuration files"
echo "📁 Files created:"
echo "   - docker-compose.certbot.yml"
echo "   - nginx-letsencrypt.conf"
echo ""
echo "🚀 To use Let's Encrypt certificates:"
echo "1. Point your domain $DOMAIN to this server's IP"
echo "2. Run: docker-compose -f docker-compose.yml -f docker-compose.certbot.yml up certbot"
echo "3. Copy nginx-letsencrypt.conf to nginx.conf"
echo "4. Run: docker-compose up -d"
echo ""
echo "📱 For development with self-signed certs, run: ./generate-ssl.sh" 