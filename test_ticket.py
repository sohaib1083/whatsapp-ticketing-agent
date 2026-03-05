#!/usr/bin/env python3
"""
Test script to verify the ticket creation functionality
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ticket.ticket_creator import TicketCreator


def test_ticket_creation():
    """Test creating a ticket"""
    print("Testing Ticket Creation...")
    print("-" * 50)
    
    # Initialize ticket creator
    creator = TicketCreator()
    
    # Test ticket data
    ticket_data = {
        'issue_description': 'Users cannot login to the CRM system. Getting "Invalid credentials" error even with correct password.',
        'system_name': 'CRM',
        'environment': 'production',
        'severity': 'critical',
        'requester': '+1234567890'
    }
    
    print(f"\nCreating ticket with data:")
    print(f"  System: {ticket_data['system_name']}")
    print(f"  Environment: {ticket_data['environment']}")
    print(f"  Severity: {ticket_data['severity']}")
    print(f"  Issue: {ticket_data['issue_description'][:50]}...")
    
    # Create ticket
    result = creator.create_ticket(ticket_data)
    
    if result['success']:
        print(f"\n✅ SUCCESS!")
        print(f"Ticket Number: {result['ticket_number']}")
        print(f"\nTicket Details:")
        for key, value in result['ticket_data'].items():
            print(f"  {key}: {value}")
    else:
        print(f"\n❌ FAILED!")
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    print("\n" + "-" * 50)
    
    # List all tickets
    print("\nListing all tickets...")
    tickets = creator.list_tickets()
    print(f"Total tickets: {len(tickets)}")
    
    for ticket in tickets:
        print(f"\n  Ticket #{ticket['ticket_number']}")
        print(f"    Status: {ticket['status']}")
        print(f"    System: {ticket['system_name']}")
        print(f"    Severity: {ticket['severity']}")


if __name__ == '__main__':
    test_ticket_creation()
