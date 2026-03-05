# WhatsApp Ticketing Integration

A WhatsApp bot that integrates with a ticketing system, allowing users to create and manage tickets through WhatsApp messages.

## Features

- 📱 WhatsApp message handling via Twilio
- ✅ Whitelist-based user validation
- 🤖 AI-powered intent detection
- 📋 Automatic ticket creation
- 📊 Ticket tracking and management
- 🔍 Context-aware responses using documentation

## Architecture

```
User → WhatsApp → Twilio Webhook → Flask App → AI Agent → Ticket Creator
                        ↓
                  Whitelist Check
                        ↓
                  Intent Detection (reads docs/)
                        ↓
                  Ticket Creation (saves to data/)
```

## Installation

1. Clone the repository:
```bash
cd /home/sohaib/Documents/projects/whatsapp-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. Set up whitelist:
```bash
# Edit config/whitelist.json with authorized phone numbers
```

## Configuration

### Environment Variables

Create a `.env` file with the following:

- `TWILIO_ACCOUNT_SID`: Your Twilio account SID
- `TWILIO_AUTH_TOKEN`: Your Twilio auth token
- `TWILIO_WHATSAPP_NUMBER`: Your Twilio WhatsApp number
- `OPENAI_API_KEY`: OpenAI API key for AI agent
- `TICKET_SYSTEM_URL`: (Optional) External ticket system URL
- `TICKET_SYSTEM_API_KEY`: (Optional) External system API key

### Whitelist Configuration

Edit `config/whitelist.json`:

```json
{
  "whitelisted_numbers": [
    "+1234567890"
  ],
  "admin_numbers": [
    "+1111111111"
  ]
}
```

## Usage

### Start the Server

```bash
python src/webhook/whatsapp_handler.py
```

The server will start on `http://localhost:5000`

### Configure Twilio Webhook

1. Go to Twilio Console → WhatsApp Sandbox
2. Set webhook URL: `https://your-domain.com/webhook/whatsapp`
3. Use ngrok for local testing: `ngrok http 5000`

### Send Messages

Users can send WhatsApp messages like:

```
"Bug in CRM production - users can't login. Critical issue."
```

The bot will:
1. Validate the user is whitelisted
2. Analyze the message using AI
3. Extract ticket information
4. Create a ticket
5. Return the ticket number

Response:
```
✅ Ticket created successfully!

📋 Ticket Number: #TKT00001
🔧 System: CRM
⚠️ Severity: critical

You will receive updates on this ticket.
```

## Project Structure

```
whatsapp-agent/
├── src/
│   ├── agent/
│   │   ├── ai_agent.py          # AI intent detection
│   │   └── whitelist.py         # User validation
│   ├── ticket/
│   │   └── ticket_creator.py    # Ticket creation
│   └── webhook/
│       └── whatsapp_handler.py  # Flask webhook handler
├── config/
│   └── whitelist.json           # Authorized numbers
├── docs/
│   └── ticketing_guide.md       # AI agent context
├── data/
│   └── tickets.json             # Created tickets
├── requirements.txt
├── .env.example
└── README.md
```

## Ticket Fields

Each ticket contains:

- `ticket_number`: Unique identifier (e.g., TKT00001)
- `issue_description`: User's description of the issue
- `system_name`: System affected (CRM, ERP, WebPortal, etc.)
- `environment`: dev, staging, or production
- `severity`: low, medium, high, or critical
- `requester`: User's phone number
- `status`: open, in_progress, resolved, closed
- `created_at`: Timestamp
- `updated_at`: Timestamp

## API Endpoints

### POST /webhook/whatsapp
Receives WhatsApp messages from Twilio

### GET /health
Health check endpoint

## Development

### Running Tests

```bash
# Add tests as needed
python -m pytest tests/
```

### Adding Documentation

Add markdown files to `docs/` directory. The AI agent will read these files for context.

### Extending the System

1. **Add new intents**: Modify `src/agent/ai_agent.py`
2. **Custom ticket fields**: Update `src/ticket/ticket_creator.py`
3. **External integrations**: Extend `TicketCreator._send_to_external_system()`

## Troubleshooting

### Webhook not receiving messages
- Check Twilio configuration
- Verify ngrok is running (for local testing)
- Check webhook URL is correct

### AI not detecting intent properly
- Update `docs/ticketing_guide.md` with more examples
- Adjust AI prompt in `ai_agent.py`

### User not whitelisted
- Add number to `config/whitelist.json`
- Restart the server

## Security

- Whitelist validation prevents unauthorized access
- Environment variables for sensitive credentials
- HTTPS recommended for production webhooks

## License

MIT License
