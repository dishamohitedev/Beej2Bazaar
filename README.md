# BeejBazaar — Module: Auth + Role System (Foundation)

This is the foundation module of the BeejBazaar platform: phone-OTP
authentication, JWT sessions, and role-based access control for all 7 user
roles (Farmer, Admin, Agronomist, Equipment Vendor, Labour Contractor,
Buyer, Government Officer).

Every later module (Farm Profile, Crop Planning, Crop Health AI, etc.)
builds on top of this: `require_roles(...)` on the backend and
`ProtectedRoute` on the frontend are the plumbing every future route will use.

## What's real vs. mocked right now

| Piece | Status |
|---|---|
| JWT issuing/verification, RBAC, rate limiting | Real, production logic |
| Phone OTP | **Mocked** — OTP is always `123456`. Swap in Firebase project ID + service account JSON in `.env` to go live. No code changes needed. |
| Database | **In-memory mock** — data resets on restart. Set `MONGO_URI` in `.env` to switch to real MongoDB Atlas. No code changes needed. |

This is intentional: the interfaces (`OTPService`, `UserRepository`) are
already production-shaped. Going live is a config change, not a rewrite.

## Run the backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```
Swagger docs: http://localhost:8000/docs

## Run the frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
App: http://localhost:5173 — login with any phone number, OTP `123456`.

## Next modules (in order, since each depends on the last)

1. **Farm Profile** (Module 1) — needs auth done ✅, adds `farms` collection
2. **Crop Planning** (Module 2) — needs Farm Profile
3. **Crop Health AI** (Module 4) — needs Farm Profile + Cloudinary + Gemini
4. Remaining modules per the original spec, in dependency order
5. 
