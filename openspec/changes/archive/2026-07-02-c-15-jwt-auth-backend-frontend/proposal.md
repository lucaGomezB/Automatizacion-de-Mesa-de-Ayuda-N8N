# Proposal: JWT Authentication Backend + Frontend

## What

Add JWT Bearer token authentication to the FastAPI backend and auth context to the React frontend. Currently the API has ZERO authentication -- every endpoint is publicly accessible. The thesis (Chapter 5, Section 5.7) claims Bearer token auth on every request, so this is a gap between what is documented and what is implemented.

## Why

The system handles potentially sensitive incident data. Without authentication, anyone with network access to the API can read, create, and modify incidents. An internal tool still needs basic access control -- at minimum, a login gate that keeps unauthorized users out.

## Governance Level

**HIGH** -- auth is security-critical. Implementation must follow best practices: bcrypt password hashing, JWT with HS256, no sensitive data in token payload, token stored in memory (not localStorage).

## Scope

### Backend (Gestion_Incidentes/)
- Simple `users` table with username + hashed_password
- Login endpoint: `POST /api/v1/auth/login` returns JWT
- JWT validation middleware via FastAPI dependency injection
- Protect all `/api/v1/incidentes/*` and `/api/v1/clasificaciones/*` routes
- Health endpoints (`/health`, `/health/db`) remain public
- Seed one admin user on first migration

### Frontend (Frontend/)
- `AuthContext` provider with `{ user, token, isAuthenticated, login, logout }`
- Login page at `/login`
- `ProtectedRoute` wrapper that redirects unauthenticated users to `/login`
- Axios interceptor to inject `Authorization: Bearer <token>` header
- Handle 401 responses by clearing auth and redirecting to login

### Out of Scope
- Role-based access control (RBAC) -- single role for all operators
- Refresh tokens -- token expires after 24 hours, user re-logs in
- User registration/management endpoints
- Session management beyond JWT expiry
