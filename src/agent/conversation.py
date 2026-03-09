"""
Conversation state manager.

Tracks per-user message history so the AI can ask follow-up questions
before creating a ticket (multi-turn support).

Sessions expire after TIMEOUT minutes of inactivity.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict

logger = logging.getLogger(__name__)

TIMEOUT = timedelta(minutes=30)
MAX_HISTORY = 12  # max messages kept per user (older ones dropped)


class ConversationManager:
    """In-memory conversation store, keyed by user phone number."""

    def __init__(self):
        self._sessions: Dict[str, dict] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_history(self, user_number: str) -> List[dict]:
        """Return the conversation history for a user, or [] if expired/new."""
        session = self._sessions.get(user_number)
        if session is None:
            return []
        if datetime.now() - session['last_active'] > TIMEOUT:
            logger.info('Conversation for %s timed out — clearing', user_number)
            del self._sessions[user_number]
            return []
        return list(session['messages'])

    def add_turn(self, user_number: str, user_text: str, assistant_text: str):
        """Append a user+assistant exchange to the history."""
        session = self._sessions.setdefault(user_number, {
            'messages': [],
            'last_active': datetime.now(),
        })
        session['messages'].append({'role': 'user',      'content': user_text})
        session['messages'].append({'role': 'assistant', 'content': assistant_text})
        session['last_active'] = datetime.now()
        # Keep only the most recent MAX_HISTORY messages
        if len(session['messages']) > MAX_HISTORY:
            session['messages'] = session['messages'][-MAX_HISTORY:]

    def clear(self, user_number: str):
        """Clear a user's history (call after ticket is created)."""
        self._sessions.pop(user_number, None)
