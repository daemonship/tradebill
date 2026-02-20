# Invoice Designer for Tradespeople

Professional invoicing built for plumbers, electricians, HVAC technicians, and other tradespeople. Generic invoice tools lack trade-specific line items, parts lists, and compliance fields — this one doesn't.

## Feedback & Ideas

> **This project is being built in public and we want to hear from you.**
> Found a bug? Have a feature idea? Something feel wrong or missing?
> **[Open an issue](../../issues)** — every piece of feedback directly shapes what gets built next.

## Status

> 🚧 In active development — not yet production ready

| Feature | Status | Notes |
|---------|--------|-------|
| Project scaffold & CI | ✅ Complete | FastAPI + React + Docker |
| User authentication | ✅ Complete | JWT, bcrypt |
| Business profile API | ✅ Complete | License, contact, trade info |
| Invoice CRUD API | ✅ Complete | Line items, totals, tax, status |
| PDF generation | ✅ Complete | WeasyPrint templates |
| Mobile-first frontend | ✅ Complete | React + Vite |
| Email delivery | 📋 Planned | Resend API |
| Stripe billing | 📋 Planned | |

## What It Solves

Self-employed tradespeople need to invoice clients quickly after a job. Generic tools (Word templates, QuickBooks) are either too basic or too complex. This app provides trade-specific invoice creation with:

- Labor, parts, and materials line item categories
- Trade type selection (plumbing, electrical, HVAC, carpentry, general)
- Compliance notes auto-populated per trade
- PDF export for sending to clients
- Invoice status tracking (draft → sent → paid)

## Who It's For

Self-employed tradespeople and small trade business owners (1–5 people).

## Tech Stack

- **Backend:** FastAPI (Python), SQLAlchemy, Alembic, PostgreSQL
- **Frontend:** React, TypeScript, Vite, Zustand
- **PDF:** WeasyPrint
- **Auth:** JWT (python-jose), bcrypt (passlib)
- **Infrastructure:** Docker, Docker Compose

## Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local dev without Docker)
- Node.js 20+ (for local frontend dev)

### Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | Secret key for JWT signing (use a long random string) |
| `RESEND_API_KEY` | Resend API key for email delivery |
| `R2_ENDPOINT_URL` | Cloudflare R2 endpoint URL |
| `R2_ACCESS_KEY_ID` | R2 access key |
| `R2_SECRET_ACCESS_KEY` | R2 secret key |
| `R2_BUCKET_NAME` | R2 bucket name for PDF storage |

### Running with Docker

```bash
docker-compose up
```

API available at `http://localhost:8000` — docs at `http://localhost:8000/docs`
Frontend available at `http://localhost:5173`

### Running Locally

**Backend:**
```bash
pip install -e .[dev]
cd backend
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
python -m pytest -q
```

## API Overview

| Endpoint | Description |
|----------|-------------|
| `POST /auth/register` | Create account |
| `POST /auth/token` | Login, get JWT |
| `GET/POST /profile` | Business profile |
| `GET/POST /invoices` | List / create invoices |
| `GET/PUT /invoices/{id}` | Get / update invoice |
| `PATCH /invoices/{id}/status` | Update invoice status |
| `GET /invoices/{id}/pdf` | Download PDF |
| `GET /invoices/templates/compliance-notes` | Trade compliance text |

---

*Built by [DaemonShip](https://github.com/daemonship) — autonomous venture studio*
