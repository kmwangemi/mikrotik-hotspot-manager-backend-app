# MikroTik Hotspot Manager — FastAPI Backend

Full-featured backend for the MikroTik Hotspot ISP Management Platform.

## Tech Stack
- **FastAPI** — web framework
- **SQLAlchemy 2.0** (async, mapped columns) — ORM
- **Alembic** — database migrations
- **Neon (PostgreSQL)** — database
- **asyncpg** — async PostgreSQL driver
- **python-jose** — JWT tokens (access + refresh)
- **passlib[bcrypt]** — password hashing
- **uv** — package manager

---

## Project Structure

```
mikrotik-backend/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── api/
│   │   └── v1/
│   │       ├── router.py        # Aggregates all routes under /api/v1
│   │       ├── dependencies/
│   │       │   └── auth.py      # Auth guards, role/permission deps
│   │       └── routes/
│   │           ├── auth.py      # /auth/*
│   │           ├── vendors.py   # /vendors/* (superadmin)
│   │           ├── routers.py   # /routers/* (vendor)
│   │           ├── profile.py   # /profile/*
│   │           ├── logs.py      # /logs/* (superadmin)
│   │           └── users.py     # /users/* (superadmin)
│   ├── core/
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── enums.py             # All enums: roles, permissions, log types
│   │   └── security.py         # JWT creation/decoding, bcrypt, OTP
│   ├── db/
│   │   ├── session.py           # Async engine + session factory
│   │   └── base.py              # TimestampMixin
│   ├── models/
│   │   ├── user.py
│   │   ├── vendor.py
│   │   ├── router.py
│   │   ├── refresh_token.py
│   │   ├── activity_log.py
│   │   └── email_verification.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── vendor.py
│   │   ├── router.py
│   │   └── activity_log.py
│   └── services/
│       ├── auth_service.py
│       ├── email_service.py
│       ├── log_service.py
│       ├── user_service.py
│       ├── vendor_service.py
│       └── router_service.py
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 001_initial.py
├── scripts/
│   └── seed.py                  # Seeds the first superadmin
├── alembic.ini
├── pyproject.toml
└── .env.example
```

---

## Setup

### 1. Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Create virtual environment & install deps
```bash
cd mikrotik-backend
uv venv
source .venv/bin/activate       # Linux/Mac
# .venv\Scripts\activate        # Windows
uv pip install -e .
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your Neon database URL, JWT secrets, SMTP credentials
```

Your Neon `.env` URLs look like:
```
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.neon.tech/dbname?sslmode=require
SYNC_DATABASE_URL=postgresql+psycopg2://user:pass@ep-xxx.neon.tech/dbname?sslmode=require
```

### 4. Run migrations
```bash
alembic upgrade head
```

### 5. Seed superadmin
```bash
uv run python -m scripts.seed
# Default: admin@mikrotik.local / Admin@1234!
```

### 6. Run server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/api/docs

---

## Auth Flow

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/login` | Login → returns access + refresh tokens |
| `POST /api/v1/auth/refresh` | Exchange refresh token for new access token |
| `POST /api/v1/auth/logout` | Revoke refresh token |
| `POST /api/v1/auth/logout-all` | Revoke all sessions |
| `POST /api/v1/auth/send-otp` | Send email OTP |
| `POST /api/v1/auth/verify-otp` | Verify OTP code |
| `POST /api/v1/auth/change-password` | Change password (authenticated) |
| `GET /api/v1/auth/me` | Get current user |

---

## Roles & Permissions

### SuperAdmin
- Manage/view all vendors
- Manage all users
- View & export all activity logs
- View all routers
- Manage system settings

### Vendor
- Manage own routers (CRUD)
- View own analytics
- Manage own hotspot users
- Manage own profile

---

## API Endpoints Summary

### Vendors (SuperAdmin only)
- `POST /api/v1/vendors` — Create vendor + admin user
- `GET /api/v1/vendors` — List vendors (paginated, filterable)
- `GET /api/v1/vendors/{id}` — Get single vendor
- `PATCH /api/v1/vendors/{id}` — Update vendor
- `PATCH /api/v1/vendors/{id}/status` — Suspend/activate
- `DELETE /api/v1/vendors/{id}` — Delete vendor

### Routers (Vendor)
- `POST /api/v1/routers` — Add router
- `GET /api/v1/routers` — List vendor's routers
- `GET /api/v1/routers/{id}` — Get router
- `PATCH /api/v1/routers/{id}` — Update router
- `DELETE /api/v1/routers/{id}` — Delete router

### Profile (Any authenticated user)
- `GET /api/v1/profile` — Get profile
- `PATCH /api/v1/profile` — Update profile
- `POST /api/v1/profile/picture` — Upload profile picture
- `DELETE /api/v1/profile/picture` — Remove profile picture

### Logs (SuperAdmin only)
- `GET /api/v1/logs` — List logs (paginated, searchable)
- `GET /api/v1/logs/export` — Export logs as CSV

### Users (SuperAdmin only)
- `GET /api/v1/users` — List all users
- `GET /api/v1/users/{id}` — Get user
- `POST /api/v1/users/superadmin` — Create superadmin
- `PATCH /api/v1/users/{id}/deactivate` — Deactivate user
- `PATCH /api/v1/users/{id}/activate` — Activate user

---

## Activity Logging

Every significant action is logged to the `activity_logs` table with:
- **Who** (user_id, user_email, user_name)
- **What** (action, details)
- **Category** (auth, vendor_management, router_management, user_management, profile, settings)
- **Status** (success, error, warning)
- **When** (created_at)
- **Where** (ip_address, user_agent)
- **Metadata** (JSON — extra context like entity IDs)

---

## Production Notes
1. Set strong `SECRET_KEY` and `REFRESH_SECRET_KEY`
2. Encrypt router API passwords in the database
3. Use Vercel Blob or S3 for profile picture storage
4. Set `DEBUG=False`
5. Enable rate limiting (e.g., slowapi)
6. Set up proper SMTP credentials
