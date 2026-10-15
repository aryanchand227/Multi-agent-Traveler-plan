# Security Architecture & Threat Model

This document outlines the security controls, authentication mechanisms, proxy handling, and incident response procedures implemented in the Multi-Agent AI Travel Planner.

---

## 1. Threat Model & Mitigations

| Threat | Impact | Implemented Mitigation |
|---|---|---|
| **API Key Theft / Leakage** | Unauthorized billing on Groq account | Groq key exists only on Render backend environment variables; never exposed to frontend bundle or logged in console. |
| **Financial / Resource Exhaustion (DoS)** | Attackers sending thousands of plan requests draining Groq balance | Multi-layered defense: daily per-user plan limit (10/day), daily app budget check ($2.00/day hard stop), concurrency semaphore (max 3 concurrent workflows), sliding-window rate limiting. |
| **Identity Spoofing** | Attacker impersonating other users by passing custom headers | Replaced unverified `X-User-ID` with cryptographically signed HS256 JWT tokens with 24-hour expiration. |
| **Insecure Direct Object Reference (IDOR)** | User A reading or modifying User B's itineraries or SSE streams | Strict ownership verification on all resource routes (`/travel/{request_id}`, `/replan`, `/clarify`, `/events`). Returns HTTP 404 or 403 if user ID does not match. |
| **IP Address Spoofing** | Bypassing rate limits using fabricated `X-Forwarded-For` | `get_client_ip()` verifies immediate peer against `trusted_proxies` before parsing forwarded headers. |
| **Payload Inflation / Memory Exhaustion** | Sending gigabyte-sized JSON payloads to crash FastAPI | `RequestBodyLimitMiddleware` rejects payloads larger than `max_request_body_bytes` (64KB) with HTTP 413. |
| **Cross-Site Scripting (XSS) & Clickjacking** | Malicious iframe embedding or MIME confusion | `SecurityHeadersMiddleware` injects `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, and HSTS. |

---

## 2. Password & Credential Security

- **Hashing Algorithm**: `bcrypt` with automatic salting (work factor 12). Plaintext passwords are never stored or logged.
- **Tokens**: JSON Web Tokens (JWT) signed with `HS256` using a secret key minimum 32 characters long.
- **Storage**: Tokens are stored in browser `localStorage` and sent via `Authorization: Bearer <token>`, with optional HTTP-only cookie support.
- **Generic Login Errors**: Failed authentication returns generic `"Invalid email or password."` to avoid account enumeration.

---

## 3. Reverse Proxy & IP Handling

Hosted platforms (Render, Cloudflare, AWS ALB) terminate TLS and forward requests to FastAPI with an `X-Forwarded-For` header.

To prevent attackers from forging `X-Forwarded-For: 8.8.8.8`:
1. If direct connection (`request.client.host`) is NOT in `TRUSTED_PROXIES` and `TRUST_ALL_PROXIES` is false, `request.client.host` is used directly.
2. When deployed on Render where internal proxy IP changes dynamically, `TRUST_ALL_PROXIES=true` enables trusted parsing of Render's proxy gateway header.

---

## 4. Key Rotation Procedure

If a Groq API key or JWT secret is accidentally exposed:

### Step 1: Revoke the Groq API Key
1. Go to [Groq Console Keys](https://console.groq.com/keys).
2. Delete the compromised key immediately.
3. Generate a new API key.

### Step 2: Update Hosting Environment
1. In Render Dashboard -> `travel-planner-api` -> **Environment**:
   - Update `LLM_API_KEY` to the new key.
   - If `JWT_SECRET_KEY` was exposed, generate a new 32+ char key:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   - Updating `JWT_SECRET_KEY` instantly invalidates all previously issued JWT tokens, logging out all sessions safely.
2. Click **Save Changes** (Render will automatically redeploy with the new secrets).
