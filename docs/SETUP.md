# 🎉 FREE WhatsApp Ticketing Agent - Setup Guide

## 💰 100% FREE - No Paid Services!

This system uses completely FREE services:
- ✅ **Groq API** - FREE tier (30 req/min, 14,400/day)
- ✅ **whatsapp-web.js** - Open source WhatsApp library (FREE)
- ✅ **Local storage** - No database costs
- ✅ **Self-hosted** - Run on your own machine

**Total Cost: $0/month** 🎊

---

## 📋 Prerequisites

1. **Node.js** (v16 or higher)
2. **Python 3.8+**
3. **WhatsApp Account** (on your phone)
4. **Groq API Key** (FREE)

---

## 🚀 Quick Start (5 minutes)

### Step 1: Get Your FREE Groq API Key

1. Go to https://console.groq.com/keys
2. Sign up (it's FREE!)
3. Create a new API key
4. Copy the key (starts with `gsk_...`)

### Step 2: Install Dependencies

```bash
cd /home/sohaib/Documents/projects/whatsapp-agent

# Install Python dependencies
pip3 install -r requirements.txt

# Install Node.js dependencies  
npm install
```

### Step 3: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Groq API key
nano .env
# Replace: GROQ_API_KEY=your_groq_api_key_here
# With your actual key from Step 1
```

### Step 4: Configure Whitelist (Optional)

Edit `config/whitelist.json` to add authorized phone numbers:

```json
{
  "allowed_numbers": [
    "1234567890",
    "9876543210"
  ]
}
```

**Note**: Phone numbers should be in format without `+` or spaces.
If you want to allow ALL numbers, make the array empty: `[]`

### Step 5: Start the System

**Terminal 1** - Start Python Backend:
```bash
python3 src/webhook/whatsapp_handler.py
```

**Terminal 2** - Start WhatsApp Bot:
```bash
npm start
```

### Step 6: Connect WhatsApp

1. A QR code will appear in Terminal 2
2. Open WhatsApp on your phone
3. Go to **Settings → Linked Devices → Link a Device**
4. Scan the QR code
5. Wait for "✅ WhatsApp Bot is ready!" message

**That's it! Your bot is now running! 🎉**

---

## 📱 Testing

Send a WhatsApp message to your own number (the one you scanned QR with):

**Example 1 - Simple ticket:**
```
My website is down
```

**Example 2 - Detailed ticket:**
```
Production database is showing high CPU usage. 
System: UserDB
Environment: production
Severity: high
```

**Example 3 - Get help:**
```
help
```

You should receive responses with ticket numbers!

---

## 🔧 How It Works

```
Your Phone (WhatsApp) 
    ↓
WhatsApp Bot (Node.js - FREE)
    ↓
Python Backend (Flask)
    ↓
Groq AI (FREE) → Intent Detection
    ↓
Ticket Created → Stored Locally
    ↓
Response sent back to WhatsApp
```

---

## 💾 Where Are Tickets Stored?

Tickets are stored locally in: `data/tickets/`

Each ticket is a JSON file like: `TICK-001.json`

You can:
- View them directly
- Parse them with scripts
- Export to your ticketing system
- Store in a database later

---

## 🛠️ Troubleshooting

### "GROQ_API_KEY not set"
- Make sure you created `.env` file
- Check the API key is correct
- Restart the Python backend

### QR Code won't scan
- Make sure you're using WhatsApp on your phone (not WhatsApp Web)
- Try closing and reopening the WhatsApp camera
- Delete `.wa_session` folder and try again

### Bot not responding
- Check both terminals are running
- Check Python backend shows "Processing message"
- Check whitelist if configured
- Check Groq API limits (30/min)

### "Module not found" errors
- Run `pip3 install -r requirements.txt` again
- Run `npm install` again
- Make sure you're in the correct directory

---

## 📊 FREE API Limits

**Groq API (FREE tier):**
- ✅ 30 requests per minute
- ✅ 14,400 requests per day
- ✅ Ultra-fast responses (~100-200ms)

**That's ~10,000 tickets per week - MORE than enough!** 🚀

---

## 🔐 Security Notes

1. **Whitelist**: Add only trusted numbers to `config/whitelist.json`
2. **Environment**: Never commit `.env` file to git
3. **Sessions**: `.wa_session` contains your WhatsApp session - keep it safe
4. **Groq Key**: Never share your API key publicly

---

## 🎯 Next Steps

- ✅ Customize ticket fields in `src/ticket/ticket_creator.py`
- ✅ Update documentation in `docs/ticketing_guide.md`
- ✅ Add more intent types in `src/agent/ai_agent.py`
- ✅ Connect to your actual ticketing system
- ✅ Add email notifications
- ✅ Deploy to a server (VPS/Cloud - can use free tiers!)

---

## 🆓 FREE Deployment Options

Want to run 24/7? Use these FREE hosting options:

1. **Oracle Cloud** - Always Free tier (VM instance)
2. **Google Cloud** - $300 free credits
3. **AWS** - Free tier (12 months)
4. **Your own computer** - Just leave it running!

---

## 💡 Pro Tips

1. **Keep sessions alive**: The WhatsApp bot will maintain connection automatically
2. **Multiple numbers**: You can link multiple devices to same WhatsApp account
3. **Groq models**: We use `llama-3.3-70b-versatile` - super fast and accurate!
4. **Ticket format**: Customize the ticket JSON structure to match your system

---

## 🆘 Need Help?

- Check `ARCHITECTURE.md` for system design
- Check `PROJECT_SUMMARY.md` for technical details
- Check Groq docs: https://console.groq.com/docs
- Check whatsapp-web.js docs: https://docs.wwebjs.dev/

---

## 🎉 Enjoy Your FREE Ticketing Bot!

No subscriptions. No credit card. No hidden costs.
Just pure automation! 🚀

---

**Made with ❤️ using only FREE and Open Source tools**
