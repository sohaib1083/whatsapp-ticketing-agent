#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║        🚀 Starting WhatsApp Ticketing System + Dashboard 🚀                 ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "This will open 2 terminals:"
echo "  1. WhatsApp Bot + Backend API"
echo "  2. React Dashboard"
echo ""
echo "Press Enter to continue..."
read

# Start backend in new terminal
gnome-terminal -- bash -c "
cd /home/sohaib/Documents/projects/whatsapp-agent && 
echo '🤖 Starting WhatsApp Bot + Backend...' &&
./start.sh
" &

sleep 3

# Start frontend in new terminal
gnome-terminal -- bash -c "
cd /home/sohaib/Documents/projects/whatsapp-agent-UI && 
echo '🎨 Installing dependencies...' &&
npm install &&
echo '' &&
echo '🎨 Starting React Dashboard...' &&
npm run dev &&
read -p 'Press Enter to close...'
" &

echo ""
echo "✅ Terminals opened!"
echo ""
echo "📱 Scan QR code in Terminal 1 with WhatsApp"
echo "🌐 Dashboard will open at http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop this script"
echo ""

wait
