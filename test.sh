#!/bin/bash

# Quick test script for WhatsApp Agent

echo "🧪 Testing WhatsApp Agent Components..."
echo ""

# Test 1: Check Python dependencies
echo "1️⃣  Testing Python dependencies..."
python3 -c "import groq, flask, flask_cors; print('   ✅ All Python packages installed')" 2>/dev/null || {
    echo "   ❌ Missing Python packages. Run: pip3 install -r requirements.txt"
    exit 1
}

# Test 2: Check Node.js dependencies
echo "2️⃣  Testing Node.js dependencies..."
if [ -d "node_modules" ]; then
    echo "   ✅ Node modules installed"
else
    echo "   ❌ Node modules not found. Run: npm install"
    exit 1
fi

# Test 3: Test AI Agent
echo "3️⃣  Testing AI Agent..."
python3 -c "from src.agent.ai_agent import AIAgent; agent = AIAgent(); print('   ✅ AI Agent works')" 2>/dev/null || {
    echo "   ❌ AI Agent failed to load"
    exit 1
}

# Test 4: Check environment
echo "4️⃣  Testing environment..."
if [ -f ".env" ]; then
    if grep -q "GROQ_API_KEY=gsk_" .env 2>/dev/null; then
        echo "   ✅ Groq API key configured"
    else
        echo "   ⚠️  Groq API key not set in .env"
    fi
else
    echo "   ⚠️  .env file not found"
fi

# Test 5: Check whitelist
echo "5️⃣  Testing whitelist..."
if [ -f "config/whitelist.json" ]; then
    echo "   ✅ Whitelist file exists"
else
    echo "   ⚠️  Whitelist file not found (will allow all numbers)"
fi

echo ""
echo "✅ All critical tests passed!"
echo ""
echo "🚀 Ready to start! Run: ./start.sh"
