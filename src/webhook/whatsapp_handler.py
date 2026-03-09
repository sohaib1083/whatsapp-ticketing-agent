"""
WhatsApp Backend Handler (FREE VERSION)
Processes messages from Node.js WhatsApp bot
No Twilio - Uses free whatsapp-web.js!
"""
import os
import sys
import json
import base64

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from src.agent.ai_agent import AIAgent
from src.agent.conversation import ConversationManager
from src.ticket.ticket_creator import TicketCreator
from src.voice.transcriber import VoiceTranscriber
from src.voice.transliterator import SmartTransliterator

load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow requests from Node.js bot

# Initialize components
ai_agent = AIAgent()
ticket_creator = TicketCreator()
conversation_manager = ConversationManager()

# Voice pipeline — reuse the same Groq client that AIAgent already has
_groq_client = ai_agent.client  # None if GROQ_API_KEY not set
voice_transcriber = VoiceTranscriber(groq_client=_groq_client)
smart_transliterator = SmartTransliterator(groq_client=_groq_client)


def _build_ticket_reply(ticket_data: dict, ticket_result: dict, note: str = '') -> str:
    """Format the ticket-created confirmation message."""
    if ticket_result['success']:
        ticket_number = ticket_result['ticket_number']
        txt  = f"✅ *Ticket Created Successfully!*\n\n"
        if note:
            txt += f"{note}\n"
        txt += f"📋 *Ticket #:* {ticket_number}\n"
        txt += f"🔧 *System:* {ticket_data.get('system_name', 'N/A')}\n"
        txt += f"🌍 *Environment:* {ticket_data.get('environment', 'N/A')}\n"
        txt += f"⚠️ *Severity:* {ticket_data.get('severity', 'N/A')}\n"
        txt += f"📝 *Issue:* {ticket_data.get('issue_description', 'N/A')}\n\n"
        txt += f"✨ You will receive updates on this ticket."
        return txt
    return f"❌ *Failed to create ticket*\n{ticket_result.get('error', 'Unknown error')}"


@app.route('/process', methods=['POST'])
def process_message():
    """Process WhatsApp text message from Node.js bot."""
    try:
        data = request.json
        message_body = data.get('message', '')
        user_number  = data.get('user_number', '')
        user_name    = data.get('user_name', 'User')

        print(f"📨 Processing message from {user_name} ({user_number}): {message_body}")

        history = conversation_manager.get_history(user_number)
        intent_result = ai_agent.process_message(message_body, user_number, history)
        intent = intent_result.get('intent')

        ticket_number = None

        if intent == 'create_ticket':
            ticket_data = intent_result.get('ticket_data', {})
            ticket_data['requester'] = f"{user_name} ({user_number})"
            ticket_result = ticket_creator.create_ticket(ticket_data)
            response_text = _build_ticket_reply(ticket_data, ticket_result)
            # Clear conversation after ticket is created
            conversation_manager.clear(user_number)
            if ticket_result['success']:
                ticket_number = ticket_result['ticket_number']
        else:
            response_text = intent_result.get(
                'response',
                "I didn't quite understand that. Could you describe your issue?",
            )
            # Save this exchange so next message has context
            conversation_manager.add_turn(user_number, message_body, response_text)

        return jsonify({
            'success': True,
            'reply': response_text,
            'intent': intent,
            'ticket_number': ticket_number,
        })

    except Exception as e:
        print(f"❌ Error processing message: {str(e)}")
        return jsonify({
            'success': False,
            'reply': "❌ An error occurred processing your request. Please try again.",
            'error': str(e)
        }), 500


@app.route('/process-voice', methods=['POST'])
def process_voice():
    """Process a WhatsApp voice note from the Node.js bot."""
    try:
        data = request.json
        audio_b64  = data.get('audio_data', '')
        mime_type  = data.get('mime_type', 'audio/ogg')
        user_number = data.get('user_number', '')
        user_name   = data.get('user_name', 'User')

        if not audio_b64:
            return jsonify({'success': False, 'reply': '⚠️ No audio data received.'}), 400

        audio_bytes = base64.b64decode(audio_b64)
        print(f"🎤 Voice note from {user_name} ({user_number}) — {len(audio_bytes)//1024}KB, {mime_type}")

        # ── Step 1: Transcribe ──────────────────────────────────────────
        transcription = voice_transcriber.transcribe(audio_bytes, mime_type)

        if not transcription.get('success') or not transcription.get('text', '').strip():
            print(f"⚠️ Transcription failed: {transcription.get('error')}")
            return jsonify({
                'success': True,
                'reply': (
                    '⚠️ Sorry, I could not transcribe your voice note. '
                    'Please send a text message describing your issue.'
                ),
            })

        raw_text      = transcription['text']
        detected_lang = transcription.get('language', 'unknown')
        trans_source  = transcription.get('source', 'unknown')
        print(f"📝 Transcribed [{detected_lang}] via {trans_source}: {raw_text}")

        # ── Step 2: Transliterate / translate if needed ─────────────────
        trans_result   = smart_transliterator.process(raw_text, detected_lang)
        processed_text = trans_result['text']

        if trans_result.get('processed'):
            print(f"🔤 Transliterated [{trans_result.get('original_language')} → Roman Urdu]: {processed_text}")
            if trans_result.get('names_detected'):
                print(f"   Names: {trans_result['names_detected']}")

        # ── Step 3: Run through AI agent (with conversation history) ────
        history = conversation_manager.get_history(user_number)
        intent_result = ai_agent.process_message(processed_text, user_number, history)
        intent = intent_result.get('intent')

        # ── Step 4: Build response ───────────────────────────────────────
        lang_note = ''
        if trans_result.get('processed'):
            lang_note = '🎤 *Via:* Voice Note (Urdu → Roman Urdu transliteration applied)\n'
        else:
            lang_note = '🎤 *Via:* Voice Note (transcribed automatically)\n'

        ticket_number = None

        if intent == 'create_ticket':
            ticket_data = intent_result.get('ticket_data', {})
            ticket_data['requester'] = f"{user_name} ({user_number})"
            ticket_data['source'] = 'voice_note'
            ticket_result = ticket_creator.create_ticket(ticket_data)
            response_text = _build_ticket_reply(ticket_data, ticket_result, note=lang_note)
            conversation_manager.clear(user_number)
            if ticket_result['success']:
                ticket_number = ticket_result['ticket_number']
        else:
            response_text = intent_result.get(
                'response',
                "I heard your voice note! Could you give more detail about the issue?"
            )
            conversation_manager.add_turn(user_number, processed_text, response_text)

        return jsonify({
            'success': True,
            'reply': response_text,
            'intent': intent,
            'ticket_number': ticket_number,
            'transcription': raw_text,
            'processed_text': processed_text,
            'language': detected_lang,
        })

    except Exception as e:
        print(f"❌ Error processing voice note: {str(e)}")
        return jsonify({
            'success': False,
            'reply': (
                "❌ Sorry, I couldn't process your voice note. "
                "Please try sending a text message."
            ),
            'error': str(e),
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
    transcription_status = 'Groq Whisper (FREE)' if _groq_client else 'Local Whisper (fallback)'
    return jsonify({
        'status': 'healthy',
        'service': 'whatsapp-agent-backend',
        'version': 'FREE',
        'ai_provider': 'Groq (FREE)',
        'whatsapp_provider': 'whatsapp-web.js (Open Source)',
        'database': 'MongoDB' if ticket_creator.db is not None else 'Local JSON',
        'voice_transcription': transcription_status,
        'transliteration': 'LLM-based (Groq)' if _groq_client else 'Disabled',
        'supported_languages': ['English', 'Urdu', 'Mixed Urdu-English'],
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
