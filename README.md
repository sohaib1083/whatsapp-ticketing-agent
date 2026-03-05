# 🎉 FREE WhatsApp Ticketing Agent

100% FREE WhatsApp automation system with AI-powered ticketing and React dashboard.

## ✨ Features

- 📱 **WhatsApp Integration** - Open-source whatsapp-web.js (no API costs)
- 🤖 **AI-Powered** - Groq API with llama-3.3-70b (14,400 free requests/day)
- 💾 **MongoDB Storage** - Cloud database with local JSON fallback
- 🎨 **React Dashboard** - Beautiful real-time UI with Tailwind CSS
- 🔒 **Whitelist Security** - Control who can create tickets
- 🎯 **Intent Detection** - AI automatically extracts ticket details
- 💰 **100% FREE** - No paid services required!

## 🚀 Quick Start

### Prerequisites

- Node.js 16+
- Python 3.8+
- WhatsApp account for QR code scanning

### Installation

```bash
# Clone and install
cd /home/sohaib/Documents/projects/whatsapp-agent
npm install
pip install -r requirements.txt

# Start backend + WhatsApp bot
./start.sh

# In separate terminal - Start React UI
cd /home/sohaib/Documents/projects/whatsapp-agent-UI
npm install
npm run dev
```

### Configuration

1. **WhatsApp**: Scan QR code on first run
2. **Whitelist**: Edit `config/whitelist.json` to add authorized numbers
3. **Environment**: `.env` file is pre-configured

## 📊 System Architecture

```
WhatsApp Message → Bot (whatsapp-web.js)
                     ↓
                  AI Agent (Groq)
                     ↓
               Ticket Creator (MongoDB)
                     ↓
              React Dashboard (Port 3000)
```

## 🌐 Access Points

- **Backend API**: http://localhost:5000
- **Dashboard UI**: http://localhost:3000
- **API Docs**: http://localhost:5000/api/tickets

## 📚 Documentation

- [Setup Guide](docs/SETUP.md) - Detailed installation instructions
- [Whitelist Guide](docs/WHITELIST.md) - Managing authorized users
- [Ticketing Guide](docs/ticketing_guide.md) - How tickets are created

## 💰 Cost Breakdown

| Service | Cost |
|---------|------|
| WhatsApp | $0 (open-source) |
| AI (Groq) | $0 (14,400 requests/day free) |
| Database (MongoDB) | $0 (Atlas free tier) |
| Hosting | $0 (local) |
| **Total** | **$0/month** |

## 🎯 Example Usage

Send WhatsApp message:
```
"The database is slow in production, urgent fix needed!"
```

AI creates ticket:
- **System**: Database
- **Environment**: Production
- **Severity**: High
- **Description**: Database performance issue
- **Ticket**: TKT00042

## 🔒 Security

- Only whitelisted numbers can create tickets
- Unauthorized users receive no response (silent rejection)
- MongoDB with TLS encryption
- Local session storage (`.wa_session/`)

## 🛠️ Tech Stack

**Backend:**
- Python 3.10 + Flask
- Groq API (AI)
- MongoDB + PyMongo
- whatsapp-web.js

**Frontend:**
- React 18 + Vite
- Tailwind CSS
- Axios
- Lucide Icons

## 📝 License

MIT License - Free for personal and commercial use

---

Made with ❤️ - 100% FREE Forever!
