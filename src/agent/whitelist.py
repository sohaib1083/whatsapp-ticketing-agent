"""
Whitelist Validation Module
Checks if a phone number is authorized to use the system
"""
import json
import os


def is_whitelisted(phone_number):
    """
    Check if a phone number is in the whitelist
    
    Args:
        phone_number: Phone number to check (without 'whatsapp:' prefix)
    
    Returns:
        bool: True if whitelisted, False otherwise
    """
    whitelist_file = os.getenv('WHITELIST_FILE', 'config/whitelist.json')
    
    try:
        with open(whitelist_file, 'r') as f:
            whitelist_data = json.load(f)
        
        whitelisted = whitelist_data.get('whitelisted_numbers', [])
        admins = whitelist_data.get('admin_numbers', [])
        
        # Check if number is in either list
        return phone_number in whitelisted or phone_number in admins
        
    except FileNotFoundError:
        print(f"Warning: Whitelist file not found at {whitelist_file}")
        return False
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in whitelist file")
        return False


def add_to_whitelist(phone_number, is_admin=False):
    """Add a phone number to the whitelist"""
    whitelist_file = os.getenv('WHITELIST_FILE', 'config/whitelist.json')
    
    try:
        with open(whitelist_file, 'r') as f:
            whitelist_data = json.load(f)
        
        if is_admin:
            if phone_number not in whitelist_data['admin_numbers']:
                whitelist_data['admin_numbers'].append(phone_number)
        else:
            if phone_number not in whitelist_data['whitelisted_numbers']:
                whitelist_data['whitelisted_numbers'].append(phone_number)
        
        with open(whitelist_file, 'w') as f:
            json.dump(whitelist_data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error adding to whitelist: {str(e)}")
        return False
