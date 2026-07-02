# Tasks: JWT Authentication Backend + Frontend

## Backend

- [x] 1. Add python-jose[cryptography] and bcrypt to `requirements.txt`
- [x] 2. Add JWT config to `app/config/settings.py` (JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES)
- [x] 3. Create `app/models/user.py` — User ORM model (id, username, hashed_password, is_active, created_at)
- [x] 4. Create `alembic/versions/003_add_users_table.py` — migration + seed admin user
- [x] 5. Create `app/schemas/auth.py` — LoginRequest, TokenResponse Pydantic models
- [x] 6. Create `app/services/auth_service.py` — verify_password, get_password_hash, create_access_token, authenticate_user
- [x] 7. Create `app/core/security.py` — OAuth2PasswordBearer scheme + get_current_user dependency
- [x] 8. Create `app/routes/auth.py` — POST /api/v1/auth/login endpoint
- [x] 9. Register auth router in `app/routes/__init__.py`
- [x] 10. Protect incidentes routes with `Depends(get_current_user)` in `app/routes/incidentes.py`
- [x] 11. Protect clasificaciones routes with `Depends(get_current_user)` in `app/routes/clasificaciones.py`
- [x] 12. Update `app/models/__init__.py` to export User model
- [x] 13. Update `.env.example` with JWT_SECRET_KEY placeholder

## Frontend

- [x] 14. Create `Frontend/src/contexts/AuthContext.tsx` — AuthProvider with login/logout
- [x] 15. Create `Frontend/src/pages/LoginPage/index.tsx` — login form
- [x] 16. Update `Frontend/src/main.tsx` — add AuthProvider, Login route, ProtectedRoute
- [x] 17. Update `Frontend/src/services/api.ts` — add auth request interceptor + 401 response interceptor

## Testing

- [x] 18. Create `Gestion_Incidentes/tests/test_auth.py` — auth integration tests (14 tests)
- [x] 19. Run full backend test suite — 202 passed, 1 pre-existing failure (unrelated)
