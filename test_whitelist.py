#!/usr/bin/env python3
"""
Test script to verify whitelist functionality
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.whitelist import is_whitelisted, add_to_whitelist


def test_whitelist():
    """Test whitelist validation"""
    print("Testing Whitelist Validation...")
    print("-" * 50)
    
    # Test numbers
    test_numbers = [
        ("+1234567890", True, "Whitelisted number"),
        ("+0987654321", True, "Whitelisted number"),
        ("+1111111111", True, "Admin number"),
        ("+9999999999", False, "Not whitelisted"),
    ]
    
    for number, expected, description in test_numbers:
        result = is_whitelisted(number)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} - {number}: {description} (Expected: {expected}, Got: {result})")
    
    print("\n" + "-" * 50)
    print("\nTesting add_to_whitelist...")
    
    # Test adding a new number
    new_number = "+5555555555"
    print(f"Adding {new_number} to whitelist...")
    
    if add_to_whitelist(new_number):
        print("✅ Successfully added")
        
        # Verify it was added
        if is_whitelisted(new_number):
            print("✅ Verified: Number is now whitelisted")
        else:
            print("❌ Error: Number not found in whitelist after adding")
    else:
        print("❌ Failed to add number")


if __name__ == '__main__':
    test_whitelist()
