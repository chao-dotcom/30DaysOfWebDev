## Part 7: SQL Injection - A Different Beast

Now let's switch gears to a completely different vulnerability: SQL Injection.

![[Pasted image 20251113133046.png]]
https://xkcd.com/327/
Image URL (for hotlinking/embedding): [https://imgs.xkcd.com/comics/exploits_of_a_mom.png](https://imgs.xkcd.com/comics/exploits_of_a_mom.png)

### The Vulnerability: String Concatenation

```javascript
// User input:
const username = req.body.username;  // "admin' OR '1'='1"

// ❌ VULNERABLE CODE:
const query = `SELECT * FROM users WHERE username='${username}'`;
// Final query:
// "SELECT * FROM users WHERE username='admin' OR '1'='1'"
//                                            ^^^^^^^^^^^^^^
//                                            This becomes PART OF THE SQL!
```

**Database executes:**
- `WHERE username='admin'` → false
- `OR '1'='1'` → TRUE (always!)
- **Result:** Returns ALL users! 💥

### Solution: Prepared Statements

```javascript
const query = 'SELECT * FROM users WHERE username=?';
db.query(query, [username]);

//   username='admin'' OR ''1''=''1'
//                    ^^  ^^    ^^  ^^
//                    Quotes are ESCAPED!
```

**Database interprets as:**
- "Find user with username literally: admin' OR '1'='1"
- No user has that name → returns empty ✓

**Key points:**
- These are parametrized queries
- Query is constructed on server, executed by passing parameters
- No string concatenation, can't modify query by injection  

| Step       | **String Concatenation (VULNERABLE)**                                               | **Prepared Statement (SECURE)**                                                       |
| ---------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **1**      | Build complete SQL string:`"SELECT * FROM users WHERE username='admin' OR '1'='1'"` | Send **template** to database:`"SELECT * FROM users WHERE username=?"`                |
| **2**      | Send **entire SQL string** to the database                                          | Database **compiles template** and understands `?` as a **data placeholder**, not SQL |
| **3**      | Database **parses the string** and executes the injected logic                      | Send **parameters separately**, e.g. `["admin' OR '1'='1"]`                           |
| **4**      | Database **executes malicious query** — returns **all users 💥**                    | Database **treats parameter as literal data**, automatically escapes quotes **✓**     |
| **Result** | ❌ **SQL Injection possible**                                                        | ✅ **SQL Injection prevented**                                                         |

### ORM: The Higher-Level Solution (Don't Use Raw SQL)

```javascript
// Without ORM (raw SQL):
const query = 'SELECT * FROM users WHERE username=?';
const [rows] = await connection.query(query, ['john']);

// With ORM (Sequelize):
const users = await User.findAll({
    where: { username: 'john' }
});
```

**ORM automatically:**
1. Generates SQL query
2. Uses prepared statements
3. Escapes all parameters
4. Returns JavaScript objects

### Why ORMs Are Safer

**With Manual SQL, it is easy to make mistakes:**

**Mistake 1:** Forgot prepared statement
```javascript
const query = `SELECT * FROM users WHERE username='${username}'`;  // 💥
```

**Mistake 2:** Mixed concatenation and prepared
```javascript
const query = `SELECT * FROM users WHERE username='${username}' AND age>?`;  // 💥
```

**With ORM it is hard to mess up:**
```javascript
const users = await User.findAll({
    where: { 
        username: req.body.username,  // ✅ Always safe
        age: { [Op.gt]: req.body.age }  // ✅ Always safe
    }
});
```

You literally cannot do SQL injection with ORMs. 

---

## Part 8: Cookie vs Authorization Header - Two Authentication Methods

Finally, let's understand the two ways to send authentication.

### Method 1: Cookie-Based (Automatic)

In cookie-based authentication, the server creates a session (e.g., with a session ID) after a successful login and sends it to the browser in a `Set-Cookie` header. The browser automatically stores this cookie and includes it in all future requests to the same domain using the `Cookie` header. The server then reads the cookie on each request, verifies the session data, and authenticates the user. This method is convenient because the browser handles storage and transmission automatically, but it's tightly coupled to the domain and can be vulnerable to CSRF if not protected properly.

**STEP 1: Login - Server sets cookie**

```javascript
// STEP 1: Login - Server sets cookie
app.post('/login', (req, res) => {
    if (valid) {
        const sessionId = 'abc123';
        sessions[sessionId] = { username: 'john', loggedIn: true };
        
        res.cookie('sessionId', sessionId, { httpOnly: true });
        //  ^^^^^^^^ Browser stores this automatically
        res.json({ success: true });
    }
});
// Response headers:
// Set-Cookie: sessionId=abc123; HttpOnly
```

**STEP 2: Future requests - Browser sends automatically**

```javascript
fetch('http://localhost:8080/profile', {
    credentials: 'include'  // ← Tell browser to send cookies
});
```

**Request headers (browser adds automatically):**
```
Cookie: sessionId=abc123
```

**STEP 3: Server validates**

```javascript
app.get('/profile', (req, res) => {
    const sessionId = req.cookies.sessionId;  // 'abc123'
    const session = sessions[sessionId];
    
    if (session?.loggedIn) {
        res.json({ username: session.username });
    }
});
```

### Method 2: Token-Based (Manual)

In token-based authentication, the server issues a signed token (often a JWT) after login and returns it in the response body. The frontend manually stores this token (e.g., in `localStorage`) and explicitly includes it in future requests via the `Authorization: Bearer <token>` header. The server verifies the token's signature and data to authenticate the user. This method gives more flexibility (e.g., for APIs and mobile apps) and is stateless on the server, but requires the client to manage token storage and renewal manually.

**STEP 1: Login - Server sends token in response body**

```javascript
const jwt = require('jsonwebtoken');

app.post('/login', (req, res) => {
    if (valid) {
        const token = jwt.sign(
            { username: 'john', userId: 123 },
            'secret_key',
            { expiresIn: '1h' }
        );
        
        res.json({ 
            success: true, 
            token: token  // ← YOU must save this!
        });
    }
});
```

**Response body:**
```json
{ "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }
```

**STEP 2: Frontend manually stores token**

```javascript
fetch('http://localhost:8080/login', { ... })
    .then(r => r.json())
    .then(data => {
        localStorage.setItem('token', data.token);
        //  ^^^^^^^^^^^^^^^ Manual storage!
    });
```

**STEP 3: Future requests - YOU manually add token**

```javascript
const token = localStorage.getItem('token');

fetch('http://localhost:8080/profile', {
    headers: {
        'Authorization': `Bearer ${token}`  // ← YOU add this!
    }
});
```

**Request headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**STEP 4: Server validates token**

```javascript
app.get('/profile', (req, res) => {
    const authHeader = req.headers.authorization;
    const token = authHeader.split(' ')[1];
    
    jwt.verify(token, 'secret_key', (err, decoded) => {
        if (!err) {
            res.json({ username: decoded.username });
        }
    });
});
```

### Comparison Table

|Aspect|🍪 Cookie|🔐 Authorization Header|
|---|---|---|
|**Storage**|Browser automatic|Manual (localStorage, state)|
|**Sending**|Automatic (if `credentials: 'include'`)|Manual (every request)|
|**Server Sets**|`Set-Cookie` header|Response body (JSON)|
|**Client Sends**|`Cookie` header (automatic)|`Authorization` header (manual)|
|**JavaScript Access**|No (if httpOnly)|Yes (you stored it)|
|**XSS Vulnerable?**|No (if httpOnly)|Yes (token in localStorage)|
|**CSRF Vulnerable?**|Yes (sent automatically)|No (must manually add)|
|**CORS Requirements**|Needs `credentials: true`|Works with regular CORS|

### Why Both Are "Credentials"

```javascript
// When you set credentials: 'include':
fetch('http://api.example.com/data', {
    credentials: 'include'
});
```

**You're telling browser:**
"Send BOTH if they exist:"
1. Any cookies for api.example.com
2. Any Authorization headers I set
3. Any client certificates configured

### Real-World: Using Both

```javascript
// Login returns both:
app.post('/login', (req, res) => {
    if (valid) {
        const sessionId = 'abc123';
        const token = jwt.sign({ userId: 123 }, 'secret');
        
        res.cookie('sessionId', sessionId, { httpOnly: true });  // For web
        res.json({ token: token });  // For mobile
    }
});

// Web app uses cookie:
fetch('/api/data', {
    credentials: 'include'  // Sends cookie
});

// Mobile app uses token:
fetch('/api/data', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
```

---

## Part 9: The Complete Security Checklist

```javascript
// 1. Cookie Security
res.cookie('sessionId', token, {
    httpOnly: true,                              // XSS protection
    secure: isProduction,                        // MITM protection
    sameSite: isProduction ? 'none' : 'lax',    // CSRF protection
    maxAge: 3600000,                            // Auto-expire
    domain: isProduction ? '.yourdomain.com' : undefined
});

// 2. CORS Configuration
app.use(cors({
    origin: 'https://myapp.com',  // Whitelist origins
    credentials: true              // Allow cookies
}));

// 3. Content Security Policy
app.use((req, res, next) => {
    res.setHeader('Content-Security-Policy', 
        "default-src 'self'; script-src 'self' https://trusted-cdn.com"
    );
    next();
});

// 4. SQL Injection Protection
// ✅ Use prepared statements or ORM
const users = await User.findAll({ where: { username } });

// 5. Input Validation
const { body, validationResult } = require('express-validator');
app.post('/login',
    body('username').isAlphanumeric(),
    body('password').isLength({ min: 8 }),
    (req, res) => { ... }
);
```

---

## Summary

### On sameSite:

"It's browser-enforced CSRF protection. `'lax'` balances security and UX by blocking cross-site POST but allowing navigation GET. `'strict'` is maximum security but breaks external links. `'none'` is for cross-domain APIs and requires HTTPS."

### On httpOnly:

"It prevents XSS cookie theft by making cookies invisible to `document.cookie`. The cookie still works for HTTP requests, but JavaScript can't access it. Combined with CSP, it's your XSS defense."

### On CORS:

"CORS controls if JavaScript can read responses, not if requests are sent. It's a controlled relaxation of Same-Origin Policy. You need both `origin` whitelist and `credentials: true` for authenticated cross-origin requests."

### On SQL Injection:

"Use prepared statements where the query structure is compiled first, then parameters are inserted as data. ORMs do this automatically. The key insight: user input must never be interpreted as SQL structure."

### On Cookie vs Token:

"Cookies are automatic but vulnerable to CSRF. Tokens are manual but immune to CSRF. Cookies need `httpOnly` for XSS protection, tokens are inherently XSS-vulnerable if stored in localStorage. Modern apps often use cookies for web, tokens for mobile."

---

_Remember: Security is layers. One protection fails, the next catches it._