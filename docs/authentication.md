# Authentication & User Accounts

The Multi-Agent AI Travel Planner features a complete, self-contained multi-user authentication system built directly into the FastAPI backend with React context integration on the frontend.

---

## 1. Authentication Endpoints

Base path: `/api/v1/auth`

| Method | Endpoint | Description | Rate Limit | Auth Required |
|---|---|---|---|---|
| `POST` | `/register` | Create a new user account | 5 / min / IP | No |
| `POST` | `/login` | Authenticate with email & password | 5 / min / IP | No |
| `GET` | `/me` | Get current authenticated user profile | 20 / min | Yes (Bearer Token) |
| `POST` | `/logout` | Clear session cookie | 20 / min | Optional |

---

## 2. API Contracts

### Register (`POST /api/v1/auth/register`)
**Request:**
```json
{
  "email": "traveler@example.com",
  "password": "SecurePassword123!",
  "display_name": "Alex Traveler"
}
```
**Response (`201 Created`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "c1f72834-8cbb-49e0-82a1-12f7cb7d5d04",
    "email": "traveler@example.com",
    "display_name": "Alex Traveler",
    "is_active": true
  }
}
```

### Login (`POST /api/v1/auth/login`)
**Request:**
```json
{
  "email": "traveler@example.com",
  "password": "SecurePassword123!"
}
```
**Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "c1f72834-8cbb-49e0-82a1-12f7cb7d5d04",
    "email": "traveler@example.com",
    "display_name": "Alex Traveler",
    "is_active": true
  }
}
```

---

## 3. SSE Progress Stream Authentication

Browser `EventSource` cannot send custom headers (`Authorization: Bearer ...`).

To maintain strict ownership checks on SSE streams:
1. When opening a stream, the frontend passes the JWT token as a query parameter:
   ```javascript
   const eventSource = new EventSource(
     `${API_BASE}/api/v1/travel/${requestId}/events?token=${token}`,
     { withCredentials: true }
   );
   ```
2. The backend dependency `extract_token_from_request` inspects:
   - `Authorization` header
   - `access_token` cookie
   - `token` query parameter
3. `stream_events` verifies that the `request_id` belongs to the decoded user ID before emitting events. If User B attempts to listen to User A's stream, the server responds with `HTTP 403 Forbidden`.

---

## 4. Frontend Integration

- **State Management**: Handled by `AuthProvider` in `frontend/src/context/AuthContext.tsx`.
- **Pages**:
  - `/login`: Clean email/password form with loading states and error banners.
  - `/register`: User sign-up with password length verification and confirmation matching.
- **Header**: Automatically reflects authentication state, displaying the user's name and a "Sign Out" button.
- **Client Requests**: All API calls made via `frontend/src/lib/api.ts` automatically attach the stored token to request headers.
