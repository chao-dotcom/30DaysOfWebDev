"""
CSRF Attack & Prevention Demonstration
Main Flask application with all routes
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config.environment import Config
from vulnerable.get_endpoint import vulnerable_transfer_get
from vulnerable.post_endpoint import vulnerable_transfer_post
from protected.csrf_token import protected_detail, protected_transfer_token
from protected.samesite_cookie import protected_transfer_samesite
from attacks.img_get_attack import attack_img_get
from attacks.iframe_post_attack import attack_iframe_post, attack_form_submit
from helpers.auth import login, logout
from helpers.balance import check_balance

app = Flask(__name__)
app.config.from_object(Config)

# ============================================
# CASE 1: Vulnerable GET Request (No Protection)
# ============================================
app.add_url_rule('/vulnerable/transfer_get', 'vulnerable_transfer_get', vulnerable_transfer_get)

# ============================================
# CASE 2: Vulnerable POST Request (Still No Protection)
# ============================================
app.add_url_rule('/vulnerable/transfer_post', 'vulnerable_transfer_post', vulnerable_transfer_post, methods=['POST'])

# ============================================
# CASE 3: Protected with CSRF Token
# ============================================
app.add_url_rule('/protected/detail', 'protected_detail', protected_detail)
app.add_url_rule('/protected/transfer_token', 'protected_transfer_token', protected_transfer_token, methods=['POST'])

# ============================================
# CASE 4: Protected with SameSite Cookie
# ============================================
app.add_url_rule('/protected/transfer_samesite', 'protected_transfer_samesite', protected_transfer_samesite, methods=['POST'])

# ============================================
# Attack Scenarios (Malicious Pages)
# ============================================
app.add_url_rule('/attack/img_get', 'attack_img_get', attack_img_get)
app.add_url_rule('/attack/iframe_post', 'attack_iframe_post', attack_iframe_post)
app.add_url_rule('/attack/form_submit', 'attack_form_submit', attack_form_submit)

# ============================================
# Helper Routes
# ============================================
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout)
app.add_url_rule('/balance', 'check_balance', check_balance)


if __name__ == '__main__':
    app.run(debug=Config.DEBUG, port=Config.PORT)

