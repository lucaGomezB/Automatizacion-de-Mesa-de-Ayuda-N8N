# Design: JWT Authentication Backend + Frontend

## Architecture Decisions

### 1. Library: `python-jose[cryptography]` for JWT

Chosen over PyJWT because `python-jose` is more actively maintained and has better support for multiple algorithms. The `[cryptography]` extra provides hardware-accelerated crypto operations.

### 2. Algorithm: HS256

Symmetric signing with a single secret key (`JWT_SECRET_KEY`). Appropriate for a single-service backend where the same service both issues and validates tokens. No need for asymmetric keys (RS256) when there is no distributed verification.

### 3. Token Expiry: 24 hours (1440 minutes)

Reasonable for an internal tool used during business hours. Longer than a typical session but shorter than "forever". If needed, this can be reduced via env var without code changes.

### 4. User Model: Simple `users` table

Single table with: `id`, `username` (unique), `hashed_password`, `is_active`, `created_at`. No roles, no profiles, no registration flow. One admin user seeded: `admin` / `admin123` (bcrypt hashed). This is an internal tool, not a multi-tenant SaaS.

### 5. Auth Flow

```
1. POST /api/v1/auth/login { username, password }
2. Backend validates credentials with passlib[bcrypt]
3. Backend returns { access_token, token_type: "bearer" }
4. Frontend stores token in React context state (NOT localStorage)
5. Frontend sends Authorization: Bearer <token> on all API requests
6. Backend validates JWT via FastAPI dependency get_current_user
7. Invalid/expired JWT returns 401
8. Frontend intercepts 401 → clears auth → redirects to /login
```

### 6. Protected Routes

| Route Prefix | Protected? | Reason |
|---|---|---|
| `/health`, `/health/db` | No | Docker health checks, monitoring |
| `/api/v1/health`, `/api/v1/health/db` | No | Same health endpoints under /api/v1 |
| `/api/v1/incidentes/*` | Yes | Core domain data |
| `/api/v1/clasificaciones/*` | Yes | Classification audit trail |
| `/api/v1/auth/login` | No | Login endpoint itself must be public |

### 7. Frontend Auth Architecture

```
main.tsx
├── QueryClientProvider
├── AuthProvider          ← NEW: wraps all routes
│   ├── BrowserRouter
│   │   ├── /login         → LoginPage (public)
│   │   ├── /              → ProtectedRoute → ReportarIncidentePage
│   │   └── /admin         → ProtectedRoute → AdministracionPage
│   │   └── *              → Navigate to /
```

- `AuthContext` provides: `{ user, token, isAuthenticated, login(username, password), logout() }`
- `ProtectedRoute` checks `isAuthenticated`, redirects to `/login` if false
- Token stored in React state (component memory), lost on page refresh
- Axios request interceptor reads token from AuthContext
- Axios response interceptor: on 401, calls `logout()`

### 8. Password Hashing: passlib[bcrypt]

Industry standard. bcrypt is resistant to GPU attacks due to its memory-hard design. passlib provides a clean Python API that abstracts the underlying algorithm.

### 9. No Refresh Tokens

Simple approach for an internal tool. Token expires after 24 hours, user must re-log in. This avoids the complexity of refresh token rotation, storage, and revocation. Acceptable for a thesis project where the user base is small and the session duration is generous.

### 10. Backend Dependency Injection

```python
# app/core/security.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    # Decode JWT, extract username, query User from DB
    # Raise 401 if invalid/expired
```

Protected routes add: `current_user: User = Depends(get_current_user)`.

## File Layout

### Backend (new files)
```
Gestion_Incidentes/
├── app/
│   ├── models/user.py              # User ORM model
│   ├── schemas/auth.py             # LoginRequest, TokenResponse
│   ├── services/auth_service.py    # verify_password, create_access_token, authenticate_user
│   ├── core/security.py            # OAuth2PasswordBearer + get_current_user
│   └── routes/auth.py              # POST /api/v1/auth/login
├── alembic/versions/003_add_users_table.py  # Migration + seed admin
└── tests/test_auth.py              # Auth integration tests
```

### Backend (modified files)
```
Gestion_Incidentes/
├── app/
│   ├── models/__init__.py          # Add User export
│   ├── config/settings.py           # Add JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
│   ├── routes/incidentes.py         # Add Depends(get_current_user)
│   ├── routes/clasificaciones.py    # Add Depends(get_current_user)
│   └── routes/__init__.py           # Register auth router
├── requirements.txt                 # Add python-jose, passlib, bcrypt
└── .env.example                     # Add JWT_SECRET_KEY
```

### Frontend (new files)
```
Frontend/src/
├── contexts/AuthContext.tsx         # Auth provider + context
└── pages/LoginPage/
    └── index.tsx                    # Login form component
```

### Frontend (modified files)
```
Frontend/src/
├── main.tsx                         # Add AuthProvider, Login route, ProtectedRoute
└── services/api.ts                  # Add auth interceptor
```

## Error Handling

### 401 Unauthorized Response
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Not authenticated"
  }
}
```

### 401 Invalid Credentials Response
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Incorrect username or password"
  }
}
```

These match the existing error envelope format `{"error": {"code": "...", "message": "..."}}` from `core/error_handlers.py`.

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `JWT_SECRET_KEY` | Yes | -- | Secret key for JWT signing (HS256) |
| `JWT_ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `JWT_EXPIRE_MINUTES` | No | `1440` | Token expiry in minutes (24h) |

## Testing Strategy

Backend tests in `tests/test_auth.py`:
1. `POST /api/v1/auth/login` with valid credentials → 200 + token
2. `POST /api/v1/auth/login` with invalid password → 401
3. `POST /api/v1/auth/login` with non-existent user → 401
4. `GET /api/v1/incidentes` without auth header → 401
5. `GET /api/v1/incidentes` with valid token → 200
6. `GET /api/v1/incidentes` with invalid token → 401
7. Health endpoints remain accessible without auth

Test infrastructure: reuse existing `conftest.py` fixtures (engine, db_session, client, seed_catalogs). Add a `seed_user` fixture that creates the admin user directly via the engine (matching the `seed_catalogs` pattern). Tests use SQLite in-memory -- no external services needed.
