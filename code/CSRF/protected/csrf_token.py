"""
CASE 3: Protected with CSRF Token
Implements proper CSRF token generation and verification
"""
import hashlib
import secrets
from datetime import datetime
from flask import request, session, redirect, url_for

def generate_csrf_token():
    """Generate CSRF token using session ID + timestamp + salt"""
    token_key = f"{session.sid}_{datetime.now().timestamp()}_{secrets.token_hex(16)}"
    token = hashlib.md5(token_key.encode('utf-8')).hexdigest()
    return token


def verify_csrf_token(client_token):
    """Verify CSRF token matches server-side token"""
    if not client_token:
        return False
    
    server_token = session.get('csrf_token')
    return client_token == server_token


def protected_detail():
    """Generate and store CSRF token"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Generate CSRF token
    csrf_token = generate_csrf_token()
    session['csrf_token'] = csrf_token
    
    # Import database here to avoid circular imports
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config.database import users_db
    
    username = session['username']
    balance = users_db[username]['balance']
    
    # Return HTML with hidden CSRF token field
    return f"""
    <h1>Account Details</h1>
    <p>User: {username}</p>
    <p>Balance: ${balance}</p>
    <form action="/protected/transfer_token" method="POST">
        <input type="hidden" name="csrf_token" value="{csrf_token}">
        <input type="text" name="txtFromAccount" value="{username}" readonly>
        <input type="text" name="txtTargetAccount" placeholder="Target Account">
        <input type="number" name="txtTransferMoney" placeholder="Amount">
        <button type="submit">Transfer</button>
    </form>
    """


def protected_transfer_token():
    """Protected transfer with CSRF token verification"""
    if 'username' not in session:
        return "Unauthorized", 401
    
    if request.method != 'POST':
        return "Invalid Method", 405
    
    # Verify CSRF token
    client_token = request.form.get('csrf_token')
    if not verify_csrf_token(client_token):
        return "CSRF Token Verification Failed!", 403
    
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
        
        # Regenerate token after use (one-time token)
        session.pop('csrf_token', None)
        
        return f"Transfer successful! {money} transferred from {from_id} to {target_id}"
    
    return "Transfer failed", 400

