"""
Helper Routes: Balance Checking
Check current balances
"""
from flask import session

def check_balance():
    """Check current balances"""
    if 'username' not in session:
        return "Unauthorized", 401
    
    # Import database here to avoid circular imports
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config.database import users_db
    
    username = session['username']
    return f"Current balance for {username}: ${users_db[username]['balance']}"

