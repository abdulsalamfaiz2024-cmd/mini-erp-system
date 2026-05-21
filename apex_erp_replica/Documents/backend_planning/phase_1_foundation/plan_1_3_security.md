# Plan 1.3: Authentication & Security Protocol (Exhaustive Detail)

## 1. Scope & Objective
This document defines the fortress around the Apex ERP. It covers identity verification, password security, session management, and role-based access control (RBAC).

---

## 2. Security Algorithms & Standards
We will strictly adhere to the following cryptographic standards:

- **Hashing**: `BCRYPT` with a work factor of 12.
- **JWT Signing**: `HMAC-SHA256` (HS256).
- **Session Tokens**: Short-lived (480 minutes) to minimize the impact of token theft.
- **Payload Headers**: Every API request must include `Authorization: Bearer <JWT_TOKEN>`.

---

## 3. The User Identity Model (`models/user.py`)
This model is the root of all security.

| Field | Type | Description |
| :--- | :--- | :--- |
| `username` | String(50) | Unique identifier for login. |
| `hashed_password` | String(255) | The salted and hashed BCrypt representation. **Never store plain text.** |
| `role` | Enum | `ADMIN`, `MANAGER`, `SALES`, `FINANCE`, `INVENTORY`, `PURCHASING`. |
| `failed_login_attempts` | Integer | Counter to trigger account lockout after 5 attempts. |
| `last_login` | DateTime | Audit field for security monitoring. |

---

## 4. The Token Lifecycle (Sequence of Events)
1. **Request**: Frontend sends `POST /api/v1/auth/login` with credentials.
2. **Verification**: 
    - `AuthManager` fetches user by username.
    - Password verified using `Passlib` (`verify_password`).
    - If fail -> Increment `failed_login_attempts` -> Return 401.
3. **Generation**: If success -> Generate JWT containing `sub` (user_id) and `scopes` (role).
4. **Delivery**: Return JSON with `access_token` and `token_type: "bearer"`.
5. **Storage**: Frontend stores token in `localStorage` or `sessionStorage` (to be decided in Phase 3).

---

## 5. Dependency Injection: `GetCurrentUser`
Every protected route (e.g., creating an order) will use a FastAPI dependency:
```python
async def get_current_active_user(token: str = Depends(oauth2_scheme)):
    # 1. Decode token
    # 2. Extract user_id
    # 3. Check DB if user is active
    # 4. Return User object
```

---

## 6. Verification Steps (The "Fortress" Protocol)
Before concluding Phase 1:
1. [ ] **Hashing Test**: Verify that a password cannot be reversed from its hash.
2. [ ] **JWT Expiry Test**: Verify that a token becomes invalid after its 480-minute window.
3. [ ] **Role Leakage Test**: Verify that a `SALES` user cannot access `/api/v1/finance/ledger`.
4. [ ] **Invalid Token Test**: Verify that a modified JWT (changed signature) is rejected with a 403 status.
