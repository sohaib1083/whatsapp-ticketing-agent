#!/bin/bash

# Setup script for WhatsApp Agent

echo "🚀 Setting up WhatsApp Ticketing Agent..."
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your credentials"
fi

# Create data directory
mkdir -p data

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Twilio and OpenAI credentials"
echo "2. Update config/whitelist.json with authorized phone numbers"
echo "3. Run: python src/webhook/whatsapp_handler.py"
echo ""
echo "For local testing with ngrok:"
echo "  ngrok http 5000"
echo ""
