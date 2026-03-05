"""
Ticket Creator Module (MongoDB Version)
Creates tickets in MongoDB database
"""
# Fix for OpenSSL 3.0.2 compatibility with MongoDB Atlas - MUST BE FIRST
import os
os.environ['OPENSSL_CONF'] = '/dev/null'

import json
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class TicketData(BaseModel):
    """Ticket data model with defaults for optional fields"""
    issue_description: str
    system_name: str = "Unknown"
    environment: str = "production"
    severity: str = "medium"
    requester: str = "Unknown"


class TicketCreator:
    """Ticket creation handler with MongoDB"""
    
    def __init__(self):
        """Initialize ticket creator with MongoDB connection"""
        self.mongo_uri = os.getenv('MONGODB_URI')
        self.db_name = os.getenv('MONGODB_DB_NAME', 'whatsapp_tickets')
        
        if not self.mongo_uri:
            print("⚠️ Warning: MONGODB_URI not set, using local JSON fallback")
            self.db = None
            self.tickets_file = 'data/tickets.json'
            self._ensure_tickets_file()
        else:
            try:
                # MongoDB connection with OpenSSL 3.0.2 compatibility fix
                self.client = MongoClient(
                    self.mongo_uri,
                    serverSelectionTimeoutMS=15000,
                    tlsInsecure=True
                )
                # Test connection
                self.client.admin.command('ping')
                self.db = self.client[self.db_name]
                self.tickets_collection = self.db['tickets']
                print(f"✅ Connected to MongoDB: {self.db_name}")
            except Exception as e:
                print(f"❌ MongoDB connection failed: {e}")
                print("   Falling back to local JSON storage")
                self.db = None
                self.tickets_file = 'data/tickets.json'
                self._ensure_tickets_file()
    
    def _ensure_tickets_file(self):
        """Ensure tickets data file exists (fallback)"""
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.tickets_file):
            with open(self.tickets_file, 'w') as f:
                json.dump([], f)
    
    def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a ticket in MongoDB or JSON fallback
        
        Args:
            ticket_data: Dictionary containing ticket information
        
        Returns:
            Dictionary with success status and ticket number
        """
        try:
            # Validate ticket data
            ticket = TicketData(**ticket_data)
            
            # Generate ticket number
            ticket_number = self._generate_ticket_number()
            
            # Prepare ticket record
            ticket_record = {
                'ticket_number': ticket_number,
                'issue_description': ticket.issue_description,
                'system_name': ticket.system_name,
                'environment': ticket.environment,
                'severity': ticket.severity,
                'requester': ticket.requester,
                'status': 'open',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Save to MongoDB or JSON
            if self.db is not None:
                self.tickets_collection.insert_one(ticket_record)
                print(f"✅ Ticket {ticket_number} saved to MongoDB")
            else:
                self._save_to_json(ticket_record)
                print(f"✅ Ticket {ticket_number} saved to local JSON")
            
            return {
                'success': True,
                'ticket_number': ticket_number,
                'ticket': ticket_record
            }
            
        except Exception as e:
            print(f"Error creating ticket: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_ticket_number(self) -> str:
        """Generate unique ticket number"""
        if self.db is not None:
            # MongoDB: count documents
            count = self.tickets_collection.count_documents({}) + 1
        else:
            # JSON: count from file
            with open(self.tickets_file, 'r') as f:
                tickets = json.load(f)
                count = len(tickets) + 1
        
        return f"TICK-{count:04d}"
    
    def _save_to_json(self, ticket_record: Dict[str, Any]):
        """Save ticket to JSON file (fallback)"""
        with open(self.tickets_file, 'r') as f:
            tickets = json.load(f)
        
        tickets.append(ticket_record)
        
        with open(self.tickets_file, 'w') as f:
            json.dump(tickets, f, indent=2)
    
    def get_all_tickets(self) -> list:
        """Get all tickets"""
        if self.db is not None:
            tickets = list(self.tickets_collection.find({}, {'_id': 0}).sort('created_at', -1))
            return tickets
        else:
            with open(self.tickets_file, 'r') as f:
                return json.load(f)
    
    def get_ticket(self, ticket_number: str) -> Dict[str, Any]:
        """Get single ticket by number"""
        if self.db is not None:
            ticket = self.tickets_collection.find_one({'ticket_number': ticket_number}, {'_id': 0})
            return ticket if ticket else {}
        else:
            with open(self.tickets_file, 'r') as f:
                tickets = json.load(f)
                for ticket in tickets:
                    if ticket['ticket_number'] == ticket_number:
                        return ticket
                return {}
    
    def update_ticket_status(self, ticket_number: str, status: str) -> bool:
        """Update ticket status"""
        try:
            if self.db is not None:
                result = self.tickets_collection.update_one(
                    {'ticket_number': ticket_number},
                    {'$set': {'status': status, 'updated_at': datetime.now().isoformat()}}
                )
                return result.modified_count > 0
            else:
                with open(self.tickets_file, 'r') as f:
                    tickets = json.load(f)
                
                for ticket in tickets:
                    if ticket['ticket_number'] == ticket_number:
                        ticket['status'] = status
                        ticket['updated_at'] = datetime.now().isoformat()
                        break
                
                with open(self.tickets_file, 'w') as f:
                    json.dump(tickets, f, indent=2)
                return True
        except Exception as e:
            print(f"Error updating ticket: {e}")
            return False
            
            # Generate ticket number
            ticket_number = self._generate_ticket_number()
            
            # Prepare ticket record
            ticket_record = {
                'ticket_number': ticket_number,
                'issue_description': ticket.issue_description,
                'system_name': ticket.system_name,
                'environment': ticket.environment,
                'severity': ticket.severity,
                'requester': ticket.requester,
                'status': 'open',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Save to local file
            self._save_ticket_locally(ticket_record)
            
            # If external ticket system is configured, send to it
            if self.ticket_system_url:
                self._send_to_external_system(ticket_record)
            
            return {
                'success': True,
                'ticket_number': ticket_number,
                'ticket_data': ticket_record
            }
            
        except Exception as e:
            print(f"Error creating ticket: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_ticket_number(self) -> str:
        """Generate a unique ticket number"""
        try:
            with open(self.tickets_file, 'r') as f:
                tickets = json.load(f)
            
            # Generate ticket number based on count
            ticket_count = len(tickets) + 1
            return f"TKT{ticket_count:05d}"
        except:
            return "TKT00001"
    
    def _save_ticket_locally(self, ticket_record: Dict[str, Any]):
        """Save ticket to local JSON file"""
        try:
            with open(self.tickets_file, 'r') as f:
                tickets = json.load(f)
            
            tickets.append(ticket_record)
            
            with open(self.tickets_file, 'w') as f:
                json.dump(tickets, f, indent=2)
                
        except Exception as e:
            print(f"Error saving ticket locally: {str(e)}")
            raise
    
    def _send_to_external_system(self, ticket_record: Dict[str, Any]):
        """Send ticket to external ticketing system"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.post(
                self.ticket_system_url,
                json=ticket_record,
                headers=headers,
                timeout=10
            )
            
            response.raise_for_status()
            print(f"Ticket sent to external system: {ticket_record['ticket_number']}")
            
        except Exception as e:
            print(f"Warning: Failed to send to external system: {str(e)}")
            # Don't fail the ticket creation if external system is down
    
    def get_ticket(self, ticket_number: str) -> Dict[str, Any]:
        """Retrieve a ticket by number"""
        try:
            with open(self.tickets_file, 'r') as f:
                tickets = json.load(f)
            
            for ticket in tickets:
                if ticket['ticket_number'] == ticket_number:
                    return ticket
            
            return None
        except Exception as e:
            print(f"Error retrieving ticket: {str(e)}")
            return None
    
    def list_tickets(self, requester: str = None) -> list:
        """List all tickets, optionally filtered by requester"""
        try:
            with open(self.tickets_file, 'r') as f:
                tickets = json.load(f)
            
            if requester:
                tickets = [t for t in tickets if t['requester'] == requester]
            
            return tickets
        except Exception as e:
            print(f"Error listing tickets: {str(e)}")
            return []
