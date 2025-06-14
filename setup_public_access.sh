#!/bin/bash

echo "🌐 Setting up public access for Cross-Mind Consensus API with GLM-4-AIR"
echo "=================================================================="

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me)
echo "📍 Public IP: $PUBLIC_IP"

# Check if API is running
if ! curl -s http://localhost:8001/health > /dev/null; then
    echo "❌ API server not running on port 8001"
    echo "Starting API server..."
    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 &
    sleep 5
fi

echo "✅ API server running on localhost:8001"

# Option 1: Simple port forwarding (if you have SSH access)
echo ""
echo "🔧 Option 1: SSH Port Forwarding (Recommended for testing)"
echo "Run this command from your local machine:"
echo "ssh -L 8001:localhost:8001 norvyn@$PUBLIC_IP"
echo "Then access: http://localhost:8001"

# Option 2: Google Cloud Firewall (if you have gcloud access)
echo ""
echo "🔧 Option 2: Google Cloud Firewall Rule"
echo "Run these commands if you have gcloud access:"
echo "gcloud compute firewall-rules create allow-api-8001 \\"
echo "  --allow tcp:8001 \\"
echo "  --source-ranges 0.0.0.0/0 \\"
echo "  --description 'Allow Cross-Mind Consensus API access'"
echo ""
echo "Then access: http://$PUBLIC_IP:8001"

# Option 3: Nginx reverse proxy
echo ""
echo "🔧 Option 3: Nginx Reverse Proxy (Production ready)"
echo "This will make the API available on port 80 (standard HTTP)"

# Check if nginx is installed
if command -v nginx > /dev/null; then
    echo "✅ Nginx is installed"
    
    # Backup existing config
    if [ -f /etc/nginx/nginx.conf ]; then
        sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)
        echo "📋 Backed up existing nginx.conf"
    fi
    
    # Copy our public config
    sudo cp config/nginx/nginx-public.conf /etc/nginx/nginx.conf
    echo "📝 Updated nginx configuration"
    
    # Test nginx config
    if sudo nginx -t; then
        echo "✅ Nginx configuration is valid"
        sudo systemctl restart nginx
        echo "🔄 Restarted nginx"
        
        # Test public access
        sleep 2
        if curl -s http://localhost/status > /dev/null; then
            echo "✅ Public access configured successfully!"
            echo "🌐 API available at: http://$PUBLIC_IP"
            echo "📚 Documentation: http://$PUBLIC_IP/docs"
            echo "🔍 Status: http://$PUBLIC_IP/status"
        else
            echo "❌ Public access test failed"
        fi
    else
        echo "❌ Nginx configuration error"
        sudo cp /etc/nginx/nginx.conf.backup.* /etc/nginx/nginx.conf 2>/dev/null || true
    fi
else
    echo "❌ Nginx not installed"
    echo "Install with: sudo apt update && sudo apt install nginx"
fi

# Update GPT configuration
echo ""
echo "🤖 Updating GPT Configuration"
echo "Update your GPT actions.yaml with:"
echo "servers:"
echo "  - url: http://$PUBLIC_IP"
echo "    description: Public API server with GLM-4-AIR"
echo "  - url: http://localhost:8001"
echo "    description: Local development server"

# Test endpoints
echo ""
echo "🧪 Testing API endpoints..."
echo "Local test:"
curl -s -H "Authorization: Bearer 87ea1604be1f6_02f173F5fb67582e647fcef6c40" \
     http://localhost:8001/models | jq -r '.models | length' 2>/dev/null && echo " models available" || echo "❌ Local API test failed"

echo ""
echo "🎉 Setup complete!"
echo "Choose one of the options above to enable public access."
echo ""
echo "💡 For GPT integration, use:"
echo "   - Local: http://localhost:8001 (with SSH tunnel)"
echo "   - Public: http://$PUBLIC_IP (after firewall/nginx setup)"
echo "   - Auth: Bearer 87ea1604be1f6_02f173F5fb67582e647fcef6c40" 