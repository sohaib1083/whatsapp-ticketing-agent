#!/bin/bash

# FREE WhatsApp Ticketing Agent - Startup Script
# This script starts both the Python backend and Node.js WhatsApp bot

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║              🎉 FREE WhatsApp Ticketing Agent 🎉                            ║"
echo "║                                                                              ║"
echo "║              💰 100% FREE - No Paid APIs Required!                          ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your Groq API key!"
    echo "   Get FREE key at: https://console.groq.com/keys"
    echo ""
    read -p "Press Enter after you've added your API key to .env..."
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed!"
    echo "   Install from: https://nodejs.org/"
    exit 1
fi

# Check if npm modules are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Check if Python dependencies are installed
echo "🐍 Checking Python dependencies..."
python3 -c "import groq" 2>/dev/null || {
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt --user
}

# Create data directories if they don't exist
mkdir -p data/tickets

echo ""
echo "✅ All dependencies installed!"
echo ""
echo "🚀 Starting services..."
echo ""

# Set PYTHONPATH to include current directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start Python backend in background
echo "1️⃣  Starting Python Backend (Port 5000)..."
PYTHONPATH=$(pwd) python3 src/webhook/whatsapp_handler.py &
PYTHON_PID=$!
echo "   ✅ Python Backend PID: $PYTHON_PID"

# Wait a bit for Python to start
sleep 3

# Check if Python backend started successfully
if ! ps -p $PYTHON_PID > /dev/null 2>&1; then
    echo "   ❌ Python Backend failed to start!"
    echo "   Check for errors above"
    exit 1
fi

# Start Node.js WhatsApp bot
echo ""
echo "2️⃣  Starting WhatsApp Bot..."
echo "   📱 Scan the QR code with your WhatsApp!"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo ""
    echo "🛑 Shutting down services..."
    kill $PYTHON_PID 2>/dev/null || true
    pkill -f "node whatsapp_bot.js" 2>/dev/null || true
    echo "✅ Services stopped"
    exit 0
}

trap cleanup EXIT INT TERM

# Start WhatsApp bot (this will block and show QR code)
npm start

# If we get here, the bot was stopped
cleanup
