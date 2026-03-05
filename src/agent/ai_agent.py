"""
AI Agent Module (FREE VERSION - Groq API)
Reads documentation and detects intent from user messages
Uses FREE Groq API - No costs!
"""
import os
import json
from typing import Dict, Any
from groq import Groq


class AIAgent:
    """AI Agent for intent detection and ticket information extraction"""
    
    def __init__(self):
        """Initialize the AI agent with FREE Groq API"""
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            print("⚠️ Warning: GROQ_API_KEY not set. Using fallback intent detection.")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)
        self.documentation = self._load_documentation()
    
    def _load_documentation(self) -> str:
        """Load markdown documentation files"""
        docs_dir = 'docs'
        documentation = ""
        
        try:
            doc_file = os.path.join(docs_dir, 'ticketing_guide.md')
            if os.path.exists(doc_file):
                with open(doc_file, 'r') as f:
                    documentation += f.read() + "\n\n"
        except Exception as e:
            print(f"Error loading documentation: {str(e)}")
        
        return documentation
    
    def process_message(self, message: str, user_number: str) -> Dict[str, Any]:
        """
        Process user message and detect intent using FREE Groq API
        
        Args:
            message: User's WhatsApp message
            user_number: User's phone number
        
        Returns:
            Dictionary with intent and extracted data
        """
        if not self.client:
            return self._simple_intent_detection(message)
            
        system_prompt = f"""You are an AI assistant for a ticketing system. Your job is to:
1. Understand the user's intent from their WhatsApp message
2. Extract ticket information if they want to create a ticket
3. Provide helpful responses

Documentation:
{self.documentation}

Analyze the user's message and respond in JSON format:
{{
    "intent": "create_ticket|greeting|help|query",
    "ticket_data": {{
        "issue_description": "...",
        "system_name": "...",
        "environment": "dev|staging|production",
        "severity": "low|medium|high|critical"
    }},
    "response": "Optional response message if not creating a ticket"
}}

If the message is unclear or missing information, ask for clarification in the response field.
"""
        
        try:
            # Using Groq's FREE llama-3.3-70b model - super fast!
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            result = json.loads(content)
            
            # Ensure ticket_data has all required fields with defaults
            if result.get('intent') == 'create_ticket' and 'ticket_data' in result:
                ticket_data = result['ticket_data']
                # Provide defaults for missing fields
                ticket_data.setdefault('system_name', 'Unknown')
                ticket_data.setdefault('environment', 'production')
                ticket_data.setdefault('severity', 'medium')
                ticket_data.setdefault('issue_description', message)
            
            return result
            
        except Exception as e:
            print(f"Error in AI processing: {str(e)}")
            # Fallback to simple intent detection
            return self._simple_intent_detection(message)
    
    def _simple_intent_detection(self, message: str) -> Dict[str, Any]:
        """Fallback simple intent detection without AI"""
        message_lower = message.lower()
        
        # Check for greetings
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return {
                'intent': 'greeting',
                'response': 'Hello! I can help you create tickets. Describe your issue and I\'ll create a ticket for you.'
            }
        
        # Check for help
        if any(word in message_lower for word in ['help', 'how to', 'guide']):
            return {
                'intent': 'help',
                'response': 'To create a ticket, send a message describing your issue. Include: system name, environment, and severity if possible.'
            }
        
        # Default: assume ticket creation
        return {
            'intent': 'create_ticket',
            'ticket_data': {
                'issue_description': message,
                'system_name': 'Unknown',
                'environment': 'production',
                'severity': 'medium'
            }
        }
