# Faculty Availability & Appointment Scheduler

A full-stack academic scheduling platform that helps students find real-time faculty availability and request appointments, while giving faculty control over office hours, leave, blocked periods, and bookings.

The system dynamically calculates bookable time slots instead of relying on pre-generated static slots.

> Built with React, TypeScript, FastAPI, PostgreSQL, SQLAlchemy, and Alembic.

---

## 📸 Preview

### Faculty Availability

![Faculty Availability](docs/screenshots/faculty-availability.png)

---
## 📌 Problem Overview

Students often struggle to know when a faculty member is actually available
for a discussion, consultation, or academic meeting.

Faculty availability can change because of:

- Regular teaching schedules
- Meetings and other commitments
- Temporary office hours
- Blocked periods
- Planned leave
- Existing appointments

Traditional systems often rely on fixed schedules or manual communication,
which can result in unnecessary back-and-forth and conflicting bookings.

This project provides a centralized system where faculty can manage their
availability and students can discover and request genuinely bookable time
slots in real time.

---

## ✨ Key Features

### 👨‍🎓 Student

- Search and browse faculty members
- View real-time faculty availability
- Select available appointment slots
- Submit appointment requests
- Track appointment status
- Cancel appointments

### 👨‍🏫 Faculty

- Manage recurring weekly office hours
- Publish one-time temporary office hours
- Create temporary blocked periods
- Declare planned leave
- Review student appointment requests
- Accept or reject requests
- Complete or cancel appointments
- Manage their consultation schedule

### 🛡️ Administrator

- View system-wide statistics
- Manage users and account status
- Manage faculty profiles
- Manage academic departments
- Maintain institutional data

### ⚙️ Scheduling Engine

- Dynamically calculate available slots
- Combine regular and temporary availability
- Apply blocked periods and leave
- Exclude active appointments
- Generate discrete bookable slots
- Handle current-day expiration
- Respect the institutional `Asia/Kolkata` timezone

---

## 🧠 Technical Highlights

### 1. Dynamic Availability Engine

The system does not store pre-generated bookable slots.

Availability is calculated dynamically from:

```text
(Regular Availability ∪ Temporary Availability)
                − Blocked Periods
                − Approved Leave
                − Active Appointments
                ↓
          Bookable Slots
```

This allows faculty availability to change without maintaining static appointment-slot records.

### 2. Concurrency-Safe Booking

When multiple students attempt to book the same slot simultaneously, the backend performs an atomic PostgreSQL transaction and locks the target faculty resource using `SELECT ... FOR UPDATE`.

The booking flow:

1. Recalculates current availability
2. Checks for conflicting appointments
3. Creates the appointment only if the slot is still available
4. Returns `409 SLOT_UNAVAILABLE` if another transaction has already reserved the slot

This provides concurrency-safe protection against double-booking.

### 3. Role-Based Access Control

The application provides separate permissions for:

- **Student**
- **Faculty**
- **Administrator**

Authorization is enforced on the backend rather than relying only on frontend route protection.

### 4. Appointment State Machine

Appointments follow a controlled lifecycle:

```text
REQUESTED
   ├── ACCEPTED ──→ COMPLETED
   │      └───────→ CANCELLED
   ├── REJECTED
   └── CANCELLED
```

Terminal states cannot be modified through invalid transitions.

### 5. Timezone-Aware Scheduling

The application uses `Asia/Kolkata` as the institutional timezone and handles current-day slot expiration using backend time calculations.

### 6. Privacy-Aware Availability

Students receive only the information required to determine whether a faculty member is available.

Sensitive internal leave information is restricted to authorized faculty and administrator views.
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
