"""
WhatsApp Backend Handler (FREE VERSION)
Processes messages from Node.js WhatsApp bot
No Twilio - Uses free whatsapp-web.js!
"""
import os
import sys
import json

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from src.agent.ai_agent import AIAgent
from src.ticket.ticket_creator import TicketCreator

load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow requests from Node.js bot

# Initialize components
ai_agent = AIAgent()
ticket_creator = TicketCreator()


@app.route('/process', methods=['POST'])
def process_message():
    """Process WhatsApp message from Node.js bot"""
    try:
        data = request.json
        message_body = data.get('message', '')
        user_number = data.get('user_number', '')
        user_name = data.get('user_name', 'User')
        
        print(f"📨 Processing message from {user_name} ({user_number}): {message_body}")
        
        # Process message with AI agent
        intent_result = ai_agent.process_message(message_body, user_number)
        
        if intent_result.get('intent') == 'create_ticket':
            # Create ticket
            ticket_data = intent_result.get('ticket_data', {})
            ticket_data['requester'] = f"{user_name} ({user_number})"
            
            ticket_result = ticket_creator.create_ticket(ticket_data)
            
            if ticket_result['success']:
                ticket_number = ticket_result['ticket_number']
                response_text = f"✅ *Ticket Created Successfully!*\n\n"
                response_text += f"📋 *Ticket #:* {ticket_number}\n"
                response_text += f"🔧 *System:* {ticket_data.get('system_name', 'N/A')}\n"
                response_text += f"🌍 *Environment:* {ticket_data.get('environment', 'N/A')}\n"
                response_text += f"⚠️ *Severity:* {ticket_data.get('severity', 'N/A')}\n"
                response_text += f"📝 *Issue:* {ticket_data.get('issue_description', 'N/A')}\n\n"
                response_text += f"✨ You will receive updates on this ticket."
            else:
                response_text = f"❌ *Failed to create ticket*\n{ticket_result.get('error', 'Unknown error')}"
        else:
            # Handle other intents (greetings, help, etc.)
            response_text = intent_result.get('response', 'I didn\'t understand that. Please describe your issue.')
        
        return jsonify({
            'success': True,
            'reply': response_text,
            'intent': intent_result.get('intent'),
            'ticket_number': ticket_result.get('ticket_number') if intent_result.get('intent') == 'create_ticket' else None
        })
        
    except Exception as e:
        print(f"❌ Error processing message: {str(e)}")
        return jsonify({
            'success': False,
            'reply': "❌ An error occurred processing your request. Please try again.",
            'error': str(e)
        }), 500


@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    """Get all tickets for frontend"""
    try:
        tickets = ticket_creator.get_all_tickets()
        return jsonify({
            'success': True,
            'tickets': tickets,
            'count': len(tickets)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tickets/<ticket_number>', methods=['GET'])
def get_ticket(ticket_number):
    """Get single ticket by number"""
    try:
        ticket = ticket_creator.get_ticket(ticket_number)
        if ticket:
            return jsonify({'success': True, 'ticket': ticket})
        else:
            return jsonify({'success': False, 'error': 'Ticket not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tickets/<ticket_number>/status', methods=['PUT'])
def update_ticket_status(ticket_number):
    """Update ticket status"""
    try:
        data = request.json
        status = data.get('status')
        if not status:
            return jsonify({'success': False, 'error': 'Status required'}), 400
        
        success = ticket_creator.update_ticket_status(ticket_number, status)
        if success:
            return jsonify({'success': True, 'message': 'Status updated'})
        else:
            return jsonify({'success': False, 'error': 'Update failed'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get ticket statistics"""
    try:
        tickets = ticket_creator.get_all_tickets()
        stats = {
            'total': len(tickets),
            'open': len([t for t in tickets if t.get('status') == 'open']),
            'closed': len([t for t in tickets if t.get('status') == 'closed']),
            'in_progress': len([t for t in tickets if t.get('status') == 'in_progress']),
            'by_severity': {
                'critical': len([t for t in tickets if t.get('severity') == 'critical']),
                'high': len([t for t in tickets if t.get('severity') == 'high']),
                'medium': len([t for t in tickets if t.get('severity') == 'medium']),
                'low': len([t for t in tickets if t.get('severity') == 'low'])
            }
        }
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'whatsapp-agent-backend',
        'version': 'FREE',
        'ai_provider': 'Groq (FREE)',
        'whatsapp_provider': 'whatsapp-web.js (Open Source)',
        'database': 'MongoDB' if ticket_creator.db is not None else 'Local JSON'
    })


if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    print("=" * 70)
    print("🚀 FREE WhatsApp Ticketing Agent - Backend Server")
    print("=" * 70)
    print(f"✅ Using FREE Groq API (llama-3.3-70b)")
    print(f"✅ Using FREE whatsapp-web.js (Open Source)")
    print(f"✅ Database: MongoDB" if ticket_creator.db is not None else "✅ Database: Local JSON")
    print(f"✅ No paid APIs required!")
    print(f"📡 Server: http://{host}:{port}")
    print(f"📡 API: http://{host}:{port}/api/tickets")
    print("=" * 70)
    print()
    
    app.run(host=host, port=port, debug=debug)
