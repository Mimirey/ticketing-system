# Ticketing System — PT Wahana Solusi Sistem Indonesia

Aplikasi web Ticketing System untuk mengelola pelaporan Bug dan Feature Request dari User kepada tim IT (PM IT & Staff IT), dibuat sebagai bagian dari Technical Test PKL/Magang.

## Tech Stack

**Backend**
- Python (FastAPI)
- PostgreSQL
- SQLAlchemy (ORM) + Alembic (migration)
- JWT Authentication (python-jose) + Passlib (bcrypt)

**Frontend**
- React.js + TypeScript
- Vite
- Tailwind CSS
- React Router
- Axios
- Recharts (chart dashboard)

## Struktur Folder

```
.
├── backend/
│   ├── app/
│   │   ├── core/          # security, dependencies (auth/RBAC), helper functions
│   │   ├── db/             # koneksi database & migrations (Alembic)
│   │   ├── models/         # model SQLAlchemy
│   │   ├── schemas/        # schema Pydantic (request/response)
│   │   ├── services/       # business logic (dashboard, dll)
│   │   ├── routers/        # endpoint API
│   │   └── main.py
│   ├── uploads/            # file attachment yang diupload (auto-generated)
│   ├── .env.example
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── api/             # fungsi call ke backend
    │   ├── components/      # komponen reusable
    │   ├── context/         # AuthContext (state login)
    │   ├── pages/            # halaman (Login, Dashboard, TicketList, dll)
    │   ├── routes/           # ProtectedRoute
    │   ├── types/            # TypeScript interfaces
    │   └── App.tsx
    └── .env.example
```

## Prasyarat

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

## Instalasi & Menjalankan — Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Buat database PostgreSQL kosong (misal `ticketing_system`), lalu salin `.env.example` menjadi `.env` dan sesuaikan isinya:

```bash
cp .env.example .env
```

Isi `.env`:
```
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=ticketing_system
DATABASE_USER=postgres
DATABASE_PASSWORD=<isi_password_postgres_anda>

SECRET_KEY=<generate_dengan_perintah_di_bawah>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Generate `SECRET_KEY` yang aman:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Jalankan migration untuk membuat seluruh tabel:
```bash
alembic upgrade head
```

Seed data role & user demo (lihat bagian **Akun Demo** di bawah untuk detail).

Jalankan server:
```bash
uvicorn app.main:app --reload
```

Backend berjalan di `http://localhost:8000`. Dokumentasi API interaktif (Swagger) tersedia di `http://localhost:8000/docs`.

## Instalasi & Menjalankan — Frontend

```bash
cd frontend
npm install
cp .env.example .env
```

Isi `.env`:
```
VITE_API_BASE_URL=http://localhost:8000
```

Jalankan dev server:
```bash
npm run dev
```

Frontend berjalan di `http://localhost:5173`.

## Akun Demo

Akun berikut otomatis dibuat oleh seed script (`app/db/seed.py`), baik saat dijalankan manual maupun otomatis via Docker Compose.

| Role | Email | Password |
|---|---|---|
| User | `user@test.com` | `123456` |
| PM IT | `pm@test.com` | `123456` |
| Staff IT | `staff@test.com` | `123456` |

> Password ini hanya untuk keperluan demo/testing, bukan representasi praktik keamanan produksi.

## Menjalankan dengan Docker (Cara Tercepat)

Cara ini menjalankan database, backend, dan frontend sekaligus tanpa perlu instalasi Python/Node/PostgreSQL manual — cukup Docker Desktop.

```bash
docker compose up --build
```

Tunggu hingga backend menampilkan log `Uvicorn running on http://0.0.0.0:8000`, lalu buka:
- Frontend: `http://localhost:5173`
- Backend Swagger: `http://localhost:8000/docs`

Database, migration, dan seed data demo (lihat tabel di atas) berjalan otomatis setiap kali container dijalankan.

Untuk menghentikan:
```bash
docker compose down        # data tetap tersimpan
docker compose down -v     # menghapus seluruh data (reset total)
```

## Role & Hak Akses (RBAC)

| Role | Hak Akses |
|---|---|
| **User** | Membuat ticket, melihat status ticket miliknya sendiri, memberi komentar & lampiran |
| **PM IT** | Melihat seluruh ticket, assign/reassign ticket ke Staff IT, mengubah prioritas, melihat Activity Log |
| **Staff IT** | Melihat ticket yang ditugaskan (sebagai PIC), mengubah status progres, komentar & menyelesaikan ticket |

## Fitur Utama

- Autentikasi JWT + Role Based Access Control (3 role)
- Ticket Management dengan nomor auto-generate (`TCK-2026-XXX`)
- Workflow status terstruktur: `Open → Assigned → In Progress → QA → Done` (dengan validasi transisi, dan lock setelah `Done`)
- Assignment & reassignment ticket oleh PM IT
- Ticket History / Audit Trail (perubahan status, PIC, priority)
- Comment system (tambah/edit/hapus komentar sendiri)
- Attachment (upload/download, dengan validasi tipe & ukuran file, akses terproteksi via endpoint API — bukan static file publik)
- Dashboard & visualisasi chart (statistik ticket per status & priority)
- Search, filter (status/priority), sort, dan pagination pada daftar ticket
- Notifikasi in-app (ticket baru, assignment, perubahan status) dengan indikator unread
- Activity Log sistem (login, buat ticket, assign, ubah status, hapus — khusus PM IT)
- Soft delete pada seluruh entitas (User, Ticket, Comment, Attachment) — data tidak dihapus permanen dari database

## Ringkasan Endpoint API

Dokumentasi lengkap & interaktif tersedia di `/docs` (Swagger UI) setelah backend berjalan. Ringkasan grup endpoint:

- `POST /auth/login`
- `GET /users/me`, `GET /users`
- `GET|POST /tickets`, `GET /tickets/{id}`, `PATCH /tickets/{id}/assign|status|priority`, `DELETE /tickets/{id}`, `GET /tickets/{id}/history`
- `GET|POST /tickets/{id}/comments`, `PATCH|DELETE /tickets/{id}/comments/{comment_id}`
- `GET|POST /tickets/{id}/attachments`, `GET /tickets/{id}/attachments/{attachment_id}/download`, `DELETE /tickets/{id}/attachments/{attachment_id}`
- `GET /dashboard/statistics`, `GET /dashboard/chart/status`, `GET /dashboard/chart/priority`
- `GET /notifications`, `GET /notifications/unread-count`, `PATCH /notifications/{id}/read`
- `GET /activity-logs`

## Catatan Pengembangan

- Validasi input diterapkan di kedua sisi: Backend (Pydantic) sebagai validator utama, dan Frontend sebagai lapisan UX tambahan.
- Percobaan akses tanpa izin (role salah, bukan pemilik data) akan ditolak backend dengan `403 Forbidden`; percobaan tanpa autentikasi ditolak dengan `401 Unauthorized`.
- File attachment disimpan secara lokal di folder `backend/uploads/` dan tidak dapat diakses langsung melalui URL publik — hanya dapat diunduh melalui endpoint API yang telah melalui pengecekan otentikasi & otorisasi.
