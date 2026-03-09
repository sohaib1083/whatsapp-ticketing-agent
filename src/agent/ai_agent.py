"""
AI Agent Module (FREE VERSION - Groq API)
Reads documentation and detects intent from user messages.
Supports multi-turn conversations: asks for missing info before creating a ticket.
"""
import os
import re
import json
from typing import Dict, Any, List, Optional
from groq import Groq


# ── System prompt ──────────────────────────────────────────────────────────────
_SYSTEM_PROMPT = """You are a WhatsApp support assistant for an IT ticketing system. Your job is to collect enough information to raise a proper support ticket through natural conversation.

=== REQUIRED BEFORE CREATING A TICKET ===
1. issue_description  — a clear description of what is broken or not working
2. system_name        — the SPECIFIC system or application affected (e.g. "Backoffice", "Merchant Onboarding", "Payment Gateway", "CRM")

=== OPTIONAL (infer from context; use defaults if not mentioned) ===
- severity   → infer from urgency words (default: medium)
- environment → default: production unless the user says otherwise

=== CONVERSATION RULES ===
1. Greeting / small talk → respond warmly and ask what their issue is.
2. Vague message (single word, "need help", "there's an issue") → ask ONE focused question.
3. User described a problem but did NOT name the specific system → ask: "Which system or application is this happening in?"
4. User answered a question with something off-topic (e.g. you asked for system name and they replied "production" or "yes" or a number) → do NOT create a ticket; politely ask the system name again.
5. Once you have BOTH a clear issue AND an explicit system name → create the ticket immediately.
6. NEVER set system_name to "Unknown" — if you don't know it, ask.
7. Ask at most ONE question per reply. Do not list multiple questions.

=== EXAMPLES OF WHEN NOT TO CREATE A TICKET ===
- User says "hi" → ask what they need
- User says "there is an issue" → ask them to describe it
- You asked "which system?" and user replied "production" → ask again: "Got it — and which system or app is affected?"
- You asked "which system?" and user replied "yes" → ask again

=== JSON RESPONSE FORMAT (respond with ONLY valid JSON, no markdown) ===
{
  "intent": "create_ticket | ask_question | greeting | help",
  "ticket_data": {
    "issue_description": "...",
    "system_name": "...",
    "environment": "dev | staging | production",
    "severity": "low | medium | high | critical"
  },
  "response": "message to send to the user (required for ask_question / greeting / help)"
}

Only include "ticket_data" when intent is "create_ticket".
Only use intent "create_ticket" when BOTH issue_description AND system_name are clearly known.
"""


class AIAgent:
    """AI Agent for intent detection and ticket information extraction."""

    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            print("⚠️  Warning: GROQ_API_KEY not set. Using fallback intent detection.")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)

    def process_message(
        self,
        message: str,
        user_number: str,
        conversation_history: Optional[List[dict]] = None,
    ) -> Dict[str, Any]:
        """
        Process a user message and return intent + data.

        Args:
            message:              The user's current message.
            user_number:          User's phone number (unused here, available for logging).
            conversation_history: Previous turns [{role, content}, ...] for multi-turn context.

        Returns:
            {intent, ticket_data?, response?}
        """
        if not self.client:
            return self._simple_intent_detection(message)

        messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.4,   # lower = more consistent JSON
                max_tokens=500,
                response_format={"type": "json_object"},  # force JSON output
            )

            content = response.choices[0].message.content.strip()
            result = self._parse_json(content)

            # Ensure ticket_data defaults when intent is create_ticket
            if result.get('intent') == 'create_ticket':
                td = result.setdefault('ticket_data', {})
                td.setdefault('issue_description', message)
                td.setdefault('system_name', 'Unknown')
                td.setdefault('environment', 'production')
                td.setdefault('severity', 'medium')
                # Guard: never fire a ticket if system is still unknown
                if td['system_name'].strip().lower() in ('', 'unknown'):
                    return {
                        'intent': 'ask_question',
                        'response': "Could you tell me which system or application is affected?",
                    }

            return result

        except Exception as e:
            print(f"Error in AI processing: {e}")
            return self._simple_intent_detection(message)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _parse_json(self, content: str) -> dict:
        """Parse JSON from model output, stripping markdown fences if present."""
        # Strip ```json ... ``` or ``` ... ``` fences
        content = re.sub(r'^```(?:json)?\s*', '', content.strip(), flags=re.IGNORECASE)
        content = re.sub(r'\s*```$', '', content.strip())
        # Find the outermost { ... } block in case there's extra prose
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            content = match.group(0)
        return json.loads(content)

    def _simple_intent_detection(self, message: str) -> Dict[str, Any]:
        """Fallback when Groq is unavailable — never creates tickets from vague input."""
        msg = message.lower().strip()

        if any(w in msg for w in ['hello', 'hi', 'hey', 'salam', 'assalam']):
            return {
                'intent': 'greeting',
                'response': "Hello! I'm here to help you raise a support ticket. Please describe your issue.",
            }

        if any(w in msg for w in ['help', 'how to', 'guide', 'what can you']):
            return {
                'intent': 'help',
                'response': (
                    "To create a ticket, describe your issue and mention which system or app is affected. "
                    "Example: 'The payment module in our CRM is throwing a 500 error in production.'"
                ),
            }

        # Too short / vague → ask for more detail
        if len(msg.split()) <= 4:
            return {
                'intent': 'ask_question',
                'response': (
                    "Could you describe the issue in more detail? "
                    "Which system is affected and what exactly is happening?"
                ),
            }

        # Has enough substance → create ticket
        return {
            'intent': 'create_ticket',
            'ticket_data': {
                'issue_description': message,
                'system_name': 'Unknown',
                'environment': 'production',
                'severity': 'medium',
            },
        }
