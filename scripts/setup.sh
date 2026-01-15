#!/bin/bash

# Setup script for Contextual Agentic AI Assistant
# This script helps you set up the project for local development

set -e

echo "🚀 Setting up Contextual Agentic AI Assistant..."

# Check prerequisites
echo "📋 Checking prerequisites..."

command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }

echo "✅ Prerequisites check passed"

# Create environment files
echo "📝 Creating environment files..."

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env - Please edit with your credentials"
else
    echo "⚠️  backend/.env already exists, skipping"
fi

if [ ! -f frontend/.env.local ]; then
    cp frontend/.env.example frontend/.env.local
    echo "✅ Created frontend/.env.local"
else
    echo "⚠️  frontend/.env.local already exists, skipping"
fi

# Generate secret key if needed
if ! grep -q "your-secret-key" backend/.env 2>/dev/null; then
    echo "✅ Secret key already configured"
else
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i.bak "s/your-secret-key-at-least-32-characters-long/$SECRET_KEY/" backend/.env
    echo "✅ Generated random secret key"
fi

echo ""
echo "⚙️  Configuration needed:"
echo "   1. Edit backend/.env with your:"
echo "      - GOOGLE_CLIENT_ID"
echo "      - GOOGLE_CLIENT_SECRET"
echo "      - OPENAI_API_KEY"
echo ""
echo "   2. Get Google OAuth credentials from:"
echo "      https://console.cloud.google.com/"
echo ""
echo "   3. Add harisankar@sentellent.com as a test user"
echo ""
echo "🐳 To start the application:"
echo "   docker-compose up --build"
echo ""
echo "📚 For deployment to AWS, see DEPLOYMENT.md"
echo ""
echo "✨ Setup complete!"
