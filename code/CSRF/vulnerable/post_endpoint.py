"""
CASE 2: Vulnerable POST Request (Still No Protection)
Vulnerable to CSRF via POST request (iframe attack)
"""
from flask import request, session

def vulnerable_transfer_post():
    """Vulnerable to CSRF via POST request (iframe attack)"""
    if 'username' not in session:
        return "Unauthorized", 401
    
    if request.method != 'POST':
        return "Invalid Method", 405
    
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

