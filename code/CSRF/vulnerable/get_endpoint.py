"""
CASE 1: Vulnerable GET Request (No Protection)
Vulnerable to CSRF via GET request
"""
from flask import request, session

def vulnerable_transfer_get():
    """Vulnerable to CSRF via GET request"""
    if 'username' not in session:
        return "Unauthorized", 401
    
    from_id = request.args.get('fromid')
    target_id = request.args.get('targetid')
    money = int(request.args.get('money', 0))
    
    # Import database here to avoid circular imports
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config.database import users_db
    
    if from_id == session['username'] and from_id in users_db and target_id in users_db:
        users_db[from_id]['balance'] -= money
        users_db[target_id]['balance'] += money
        return f"Transfer successful! {money} transferred from {from_id} to {target_id}"
    
    return "Transfer failed", 400

