# Faculty Availability & Appointment Scheduler

A full-stack, enterprise-grade academic scheduling platform designed to solve the complexity of faculty office hours, ad-hoc availability, leave management, and appointment bookings in institutional environments.

Built with **FastAPI**, **PostgreSQL**, **SQLAlchemy 2.0**, **Alembic**, **React 18**, **TypeScript**, and **TanStack Query**.

---

## 📸 Preview

### Faculty Availability

![Faculty Availability](docs/screenshots/faculty-availability.png)

---
## 📌 Problem Overview

In academic institutions, coordinating student-faculty meetings is often fragmented across emails, paper sign-up sheets, and conflicting calendars:
1. **Dynamic Availability Shifts**: Faculty schedules fluctuate weekly due to exams, departmental committees, guest lectures, and planned leave.
2. **Double-Booking & Race Conditions**: Popular office hour slots often receive simultaneous booking requests from multiple students.
3. **Privacy & Administrative Overhead**: Leave records and personal reasons must remain private while accurately blocking student appointments.

The **Faculty Availability & Appointment Scheduler** solves this with a **5-Tier Continuous Interval Algebra Engine** and **Transactional Row-Level Locking**, guaranteeing real-time slot calculation and zero double-bookings.

---

## 🚀 Key Features

### 🎓 Student Portal
- **Faculty Discovery**: Search faculty by name, department, title, meeting mode, or research specialization.
- **Real-Time Availability Calendar**: Dynamic 7-day quick selector querying calculated 30-minute office hour slots in real time.
- **Conflict-Resilient Booking**: Instant validation preventing appointment overlaps.
- **Appointment Tracking & History**: Tabbed overview (*All*, *Confirmed*, *Pending*, *Completed*, *Cancelled*).
- **Self-Service Cancellation**: Releases booked slots back into the public availability pool immediately.

### 👨‍🏫 Faculty Portal
- **Recurring Weekly Office Hours**: Set recurring weekly schedules by day-of-week (0=Monday to 6=Sunday).
- **Pop-up Office Hours**: One-time extra office hour windows for specific dates (e.g. before midterms).
- **Temporary Blocked Periods**: Block busy windows for thesis defenses, seminars, or meetings.
- **Leave Declarations**: Planned absence management (`FULL_DAY`, `HALF_DAY_MORNING`, `HALF_DAY_AFTERNOON`, `MULTI_DAY`).
- **Appointment Requests Management**: 1-click **Accept** (with optional student preparation notes) and **Reject** (with reason).
- **Schedule & Attendance**: Calendar view with **Mark Completed** verification.

### 🛡️ Administrator Portal
- **Governance Dashboard**: Institutional metrics (total users, active accounts, department counts).
- **User Management**: Activate/suspend user accounts and create new student/faculty/admin profiles.
- **Faculty Directory**: Institutional overview of faculty members and department affiliations.
- **Department Management**: CRUD operations for academic departments and campus building allocations.

---

## 📐 System Architecture & Availability Algebra

### Dynamic Availability Formula
Instead of statically generating calendar slots, availability is dynamically computed on-demand using continuous interval set operations:

$$\mathcal{A}_{\text{final}} = \Big( \big( \mathcal{R} \cup \mathcal{T} \big) \setminus \mathcal{B} \Big) \setminus \Big( \mathcal{L} \cup \mathcal{P} \cup \mathcal{C} \Big)$$

- **$\mathcal{R}$ (Regular)**: Recurring weekly office hours for the requested day-of-week.
- **$\mathcal{T}$ (Temporary)**: Extra pop-up hours for the specific date.
- **$\mathcal{B}$ (Blocks)**: Temporary blocked periods.
- **$\mathcal{L}$ (Leave)**: Approved faculty leaves.
- **$\mathcal{P}$ (Pending)** & **$\mathcal{C}$ (Confirmed)**: Existing appointment reservations.

### PostgreSQL Concurrency Protection
To prevent double-booking race conditions during simultaneous requests, the backend employs **PostgreSQL Row-Level Locking (`SELECT ... FOR UPDATE`)** on the target `Faculty` record. This serializes concurrent booking transactions, ensuring exactly one student succeeds while subsequent conflicting requests receive a `409 Conflict (SLOT_UNAVAILABLE)` error.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | Python 3.13, FastAPI | High-performance asynchronous REST API |
| **ORM & DB** | PostgreSQL, SQLAlchemy 2.0, Alembic | Relational database layer with schema migrations |
| **Security** | JWT (HS256), bcrypt | Token authentication, password hashing, and server-side RBAC |
| **Frontend** | React 18, TypeScript (Strict Mode), Vite | Component-driven, type-safe web application |
| **Styling** | Tailwind CSS, Lucide React | Modern academic design system |
| **Data Fetching**| TanStack Query (React Query v5) | Server-state caching and automated query invalidation |
| **Client Routing**| React Router v6 | Role-based protected routing |
| **Testing** | Pytest, Vitest, Testing Library | Comprehensive unit, integration, and concurrency test suites |

---

## 💻 Local Development Setup

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL (optional for local SQLite development)

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Run database migrations
alembic upgrade head

# Seed initial development data (Admin, Faculty, Students, Departments)
python scripts/seed_data.py

# Start backend server
uvicorn app.main:app --reload --port 8000
```
Backend API will be live at [http://127.0.0.1:8000](http://127.0.0.1:8000). Interactive Swagger documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env

# Start frontend dev server
npm run dev
```
Frontend application will be accessible at [http://localhost:5173](http://localhost:5173).

---

## 🔑 Demo & Test Credentials

The seed script creates pre-configured demo accounts for all roles:

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@institution.edu` | `AdminPassword123!` | System Administrator |
| **Faculty** | `prof.sharma@institution.edu` | `FacultyPassword123!` | Dr. Rajesh Sharma (CS Dept, Turing Hall 301) |
| **Faculty** | `prof.menon@institution.edu` | `FacultyPassword123!` | Dr. Ananya Menon (Math Dept, Euler Block 204) |
| **Student** | `student.alex@institution.edu` | `StudentPassword123!` | Alex Rivera (Computer Science Major) |
| **Student** | `student.priya@institution.edu` | `StudentPassword123!` | Priya Patel (Data Science Major) |

*(The login screen includes 1-click credential selector buttons for instant demo access).*

---

## 🧪 Automated Testing

### Backend Test Suite (Pytest)
```bash
cd backend
pytest -v
```
**Results**: 73 passed unit/integration tests verifying RBAC, IDOR isolation, availability algebra, slot generation, appointment lifecycle, and transaction rollback.

### Frontend Test Suite (Vitest)
```bash
cd frontend
npm test
```
**Results**: 20 passed tests covering date formatters, status badges, ErrorBoundary, RBAC route guards, faculty management rendering, and booking modal conflict states.

### Frontend Production Build
```bash
cd frontend
npm run build
```

---

## 🚢 Production Deployment

### Production Checklist
1. **Environment Variables**: Set `ENVIRONMENT=production`, secure `JWT_SECRET_KEY` (min 32 chars), and configure `DATABASE_URL` with your production PostgreSQL instance.
2. **CORS Origins**: Restrict `CORS_ORIGINS` to the exact deployed frontend origin (e.g. `https://scheduler.institution.edu`).
3. **Database Migrations**: Execute `alembic upgrade head` in your CI/CD deployment pipeline before starting application workers.
4. **Health Checks**: Monitor system health at `GET /health` and database connectivity at `GET /health/db`.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
