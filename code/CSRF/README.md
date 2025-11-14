# CSRF Attack & Prevention Demonstration

This project demonstrates CSRF (Cross-Site Request Forgery) attacks and different prevention mechanisms using Flask.

## Project Structure

```
CSRF/
├── app.py                 # Main Flask application
├── config/                # Configuration files
│   ├── environment.py    # Environment and Flask config
│   └── database.py       # Mock database
├── vulnerable/            # Vulnerable endpoints (no protection)
│   ├── get_endpoint.py   # Case 1: Vulnerable GET
│   └── post_endpoint.py  # Case 2: Vulnerable POST
├── protected/             # Protected endpoints
│   ├── csrf_token.py     # Case 3: CSRF token protection
│   └── samesite_cookie.py # Case 4: SameSite cookie protection
├── attacks/              # Attack scenario pages
│   ├── img_get_attack.py # Image tag GET attack
│   └── iframe_post_attack.py # Iframe POST attack
├── helpers/              # Helper routes
│   ├── auth.py          # Login/logout
│   └── balance.py       # Balance checking
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Cases Demonstrated

### Case 1: Vulnerable GET Request
- Simple GET endpoint that accepts parameters via query string
- No CSRF protection
- Vulnerable to image tag attacks

### Case 2: Vulnerable POST Request
- POST endpoint with form data
- Still vulnerable to iframe attacks
- Shows that just using POST isn't enough

### Case 3: Protected with CSRF Token
- Implements proper CSRF token generation and verification
- Token generated using session ID + timestamp + salt with MD5
- Token stored both client-side (hidden field) and server-side (session)
- One-time token that's cleared after use

### Case 4: Protected with SameSite Cookie
- Modern approach using SameSite cookie attribute
- Automatically prevents cross-site requests

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access the application at `http://localhost:5000`

## Usage

1. **Login**: Visit `/login` and use credentials:
   - Username: `Arvin`, Password: `password123`
   - Username: `Channy`, Password: `password456`

2. **Test Vulnerable Endpoints**:
   - Visit `/attack/img_get` to see GET attack
   - Visit `/attack/iframe_post` to see POST attack

3. **Test Protected Endpoints**:
   - Visit `/protected/detail` for CSRF token protected form
   - Try the SameSite protected endpoint

4. **Check Balance**: Visit `/balance` to see current account balance

## Attack Scenarios

The attack pages demonstrate how malicious sites can exploit vulnerable endpoints:
- **Image GET Attack**: Hidden image tag triggers GET request
- **Iframe POST Attack**: Hidden iframe with form auto-submits POST request

## Protection Mechanisms

- **CSRF Tokens**: Server-generated tokens that must match on each request
- **SameSite Cookies**: Browser-enforced protection that prevents cross-site cookie sending

