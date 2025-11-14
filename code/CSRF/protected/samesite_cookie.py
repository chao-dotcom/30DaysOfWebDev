"""
CASE 4: Protected with SameSite Cookie
Modern approach using SameSite cookie attribute
Automatically prevents cross-site requests
"""
from flask import request, session

def protected_transfer_samesite():
    """Protected with SameSite cookie attribute"""
    if 'username' not in session:
        return "Unauthorized", 401
    
    # SameSite cookies prevent CSRF automatically
    # Set in app configuration: SESSION_COOKIE_SAMESITE = 'Lax' or 'Strict'
    
    from_id = request.form.get('txtFromAccount')
    target_id = request.form.get('txtTargetAccount')
    money = int(request.form.get('txtTransferMoney', 0))
    
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

