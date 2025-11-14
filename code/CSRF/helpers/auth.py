"""
Helper Routes: Authentication
Login and logout functionality
"""
import secrets
from flask import request, session, redirect, url_for

def login():
    """Login route"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Import database here to avoid circular imports
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from config.database import users_db
        
        if username in users_db and users_db[username]['password'] == password:
            session['username'] = username
            session.sid = secrets.token_hex(16)
            return redirect(url_for('protected_detail'))
        
        return "Invalid credentials", 401
    
    return """
    <form method="POST">
        <input type="text" name="username" placeholder="Username">
        <input type="password" name="password" placeholder="Password">
        <button type="submit">Login</button>
    </form>
    """


def logout():
    """Logout route"""
    session.clear()
    return redirect(url_for('login'))

