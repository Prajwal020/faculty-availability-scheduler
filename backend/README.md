# Faculty Availability & Appointment Scheduler — Backend API

This is the backend service for the **Faculty Availability & Appointment Scheduler**, implementing the technical architecture, security foundations, dynamic availability engine, and the **Appointment & Booking Engine** across Phases 1, 2, 3, 4, and 4.1.

---

## 🛠️ Technology Stack & Test Separation

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+)
- **ORM:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Migrations:** [Alembic](https://alembic.sqlalchemy.org/)
- **Database Responsibilities:**
  - **SQLite (`sqlite:///:memory:` / local file):** Used for fast local development, unit tests, interval algebra verification, state-machine validation, and standard API tests. *(Note: SQLite does not provide production-equivalent concurrency behavior).*
  - **PostgreSQL (`postgresql://...`):** Used for production deployments, transaction serialization, row-level locking (`FOR UPDATE`), and production-grade concurrency protection.
- **Security:** Pure native `bcrypt` password hashing & signed JWT access tokens (`python-jose`)
- **Validation:** [Pydantic v2](https://docs.pydantic.dev/)
- **Testing:** [Pytest](https://docs.pytest.org/) & HTTPX

---

## ⚙️ The Dynamic Faculty Availability Engine

The core scheduling engine dynamically answers:
> **"When is a particular faculty member actually available to meet a student on a target date?"**

Availability is computed on-the-fly via pure set-theoretic interval algebra without storing static slot records in the database.

### 1. The Dynamic Availability Formula

$$\mathcal{A}_{\text{final}} = \Big( \big( \mathcal{R} \cup \mathcal{T} \big) \setminus \mathcal{B} \Big) \setminus \Big( \mathcal{L} \cup \mathcal{P} \cup \mathcal{C} \Big)$$

#### Components:
- $\mathcal{R}$ = **Regular Recurring Availability:** Base recurring weekly schedule defined by the faculty member.
- $\mathcal{T}$ = **Temporary Availability:** One-time pop-up office hours. Functions completely independently on any calendar date, even when no regular weekly hours exist on that day.
- $\mathcal{B}$ = **Temporary Blocked Periods:** Unavailability windows subtracted from all available windows.
- $\mathcal{L}$ = **Approved Leave:** Hard exclusion overriding both regular and temporary availability.
- $\mathcal{P}$ = **Pending / Requested Appointments:** Active reservation intervals awaiting faculty review.
- $\mathcal{C}$ = **Confirmed / Accepted Appointments:** Active booked appointment intervals.

#### Calculation Steps:
1. **Base Availability:** Combine regular weekly availability ($\mathcal{R}$) with any one-time temporary availability ($\mathcal{T}$).
2. **Apply Blocks:** Subtract temporary blocked periods ($\mathcal{B}$).
3. **Apply Leave:** Subtract approved leave ($\mathcal{L}$).
4. **Apply Active Appointments:** Subtract pending requests ($\mathcal{P}$) and confirmed bookings ($\mathcal{C}$).
5. **Generate Available Windows:** Produce minimal, sorted, continuous available time intervals.
6. **Generate Bookable Slots:** Slice continuous windows into discrete, bookable appointment units.

---

### 2. The 5-Tier Precedence Hierarchy

The engine evaluates scheduling intervals according to the following precedence hierarchy:

```text
1. Active Appointments (Tier 1 / Hard Reservation) — Pending (REQUESTED) & Confirmed (ACCEPTED) bookings
                 ↓
2. Approved Leave (Tier 2 / Hard Exclusion) — Overrides ALL regular & temporary availability
                 ↓
3. Temporary Blocks (Tier 3 / Exclusion) — Subtracted from both regular and temporary windows
                 ↓
4. Temporary Availability (Tier 4 / Additional Availability) — One-time pop-up office hours
                 ↓
5. Regular Weekly Availability (Tier 5 / Base Schedule) — Base recurring hours
```

---

## 📅 The Appointment & Booking Engine (Phase 4 & 4.1)

### 1. Appointment State Machine

```text
               ┌─────────────┐
               │  REQUESTED  │ (Student requests slot)
               └──────┬──────┘
                      │
         ┌────────────┼────────────┐
         │ (Accept)   │ (Reject)   │ (Cancel)
         ▼            ▼            ▼
   ┌──────────┐  ┌──────────┐  ┌───────────┐
   │ ACCEPTED │  │ REJECTED │  │ CANCELLED │
   └─────┬────┘  └──────────┘  └───────────┘
         │
   ┌─────┴─────┐
   │ (Complete)│ (Cancel)
   ▼           ▼
┌───────────┐ ┌───────────┐
│ COMPLETED │ │ CANCELLED │
└───────────┘ └───────────┘
```

- **Terminal States:** `REJECTED`, `CANCELLED`, `COMPLETED`. No further state mutations are permitted.
- **Dynamic Slot Release:** When an appointment transitions to `REJECTED` or `CANCELLED`, the slot is immediately released and becomes bookable in real-time.

---

### 2. Concurrency-Safe Booking Architecture

Concurrency safety is enforced through an **atomic booking transaction and PostgreSQL row-level locking on the parent `Faculty` resource**:

```text
Student Submits Request (POST /api/v1/appointments)
                    ↓
[1] Authenticate Student & Validate Date/Time
                    ↓
[2] Begin Atomic Database Transaction
                    ↓
[3] Acquire Row Lock on Target Faculty (SELECT ... FROM faculty WHERE id = :id FOR UPDATE)
    └── Serializes concurrent booking requests for this faculty member across transactions
                    ↓
[4] Recalculate Bookable Slots via Availability Engine (Zero client trust)
    ├── If Slot Not in Available Windows → ROLLBACK & Return 409 (SLOT_UNAVAILABLE)
    └── If Slot Available → Proceed
                    ↓
[5] Query Conflicting Active Appointments (start < end_time AND end > start_time)
    ├── If Conflict Exists → ROLLBACK & Return 409 (SLOT_UNAVAILABLE)
    └── If No Conflict → Proceed
                    ↓
[6] Insert Appointment with status = REQUESTED
                    ↓
[7] Commit Transaction & Release Lock → Return 201 Created
```

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.11 or higher
- PostgreSQL (Production / Concurrency verification) or SQLite (Local development)

### 2. Installation

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Environment Configuration

Copy the example environment configuration:
```bash
cp .env.example .env
```

Configure your `.env` parameters:
```ini
ENVIRONMENT=development
DATABASE_URL=sqlite:///./faculty_scheduler.db
JWT_SECRET_KEY=your_super_secret_jwt_key_min_32_chars
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
TIMEZONE=Asia/Kolkata
```

### 4. Database Migrations

Apply database schema migrations:
```bash
alembic upgrade head
```

### 5. Seed Development Data

Populate the database with sample departments, administrator, faculty members, regular availability schedules, students, and sample appointments:
```bash
python scripts/seed_data.py
```

### 6. Start the API Server

Run the development server with Hot Reloading:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 🧪 Automated Testing

Run the automated Pytest test suite:
```bash
pytest -v
```

### Test Suite Execution Summary:
- **Total Tests:** 73
- **Passed:** 72 (100% of runnable tests)
- **Skipped:** 1 (`test_concurrency_postgres.py` requires a running PostgreSQL instance specified in `TEST_POSTGRESQL_URL`)
- **Failed:** 0

#### Test Suite Breakdown:
- **Authentication & RBAC (`test_auth.py`, `test_authorization.py`):** 14 tests
- **Departments & User Management (`test_departments.py`, `test_users.py`):** 16 tests
- **Pure Interval Algebra & Scheduling Engine (`test_scheduling_engine.py`):** 20 tests
- **Availability & Leave REST APIs (`test_availability_api.py`):** 9 tests
- **Appointment Lifecycle & Security (`test_appointments.py`):** 9 tests
- **Transactional Rollback, Stale Data, & Concurrency (`test_concurrency.py`):** 4 tests
- **Dedicated PostgreSQL Concurrency Verification (`test_concurrency_postgres.py`):** 1 test (conditionally enabled)

---

## 📖 Interactive API Documentation

Once the server is running, open your browser to access:
- **Swagger UI (Interactive):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🔑 Development Seed Accounts

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@institution.edu` | `AdminPassword123!` | System Administrator |
| **Faculty** | `prof.sharma@institution.edu` | `FacultyPassword123!` | Dr. Rajesh Sharma (CS Dept, Mon/Wed/Fri hours) |
| **Faculty** | `prof.menon@institution.edu` | `FacultyPassword123!` | Dr. Ananya Menon (MATH Dept, Tue/Thu hours) |
| **Student** | `student.alex@institution.edu` | `StudentPassword123!` | Alex Rivera (CS Major, STU-2026-001) |
| **Student** | `student.priya@institution.edu` | `StudentPassword123!` | Priya Patel (Data Science Major, STU-2026-002) |
