# Faculty Availability & Appointment Scheduler — Architecture Specification

This document provides a comprehensive technical architecture overview of the **Faculty Availability & Appointment Scheduler**, a production-grade full-stack platform built with FastAPI, PostgreSQL/SQLAlchemy, React, TypeScript, and TanStack Query.

---

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph ClientLayer ["Client Layer (React 18 + TypeScript)"]
        StudentPortal["Student Portal<br/>(Discovery, Slot Booking, Tracking)"]
        FacultyPortal["Faculty Portal<br/>(Recurring Hours, Leaves, Approvals)"]
        AdminPortal["Admin Portal<br/>(User Management, Depts, Governance)"]
    end

    subgraph APILayer ["FastAPI REST Gateway (Uvicorn ASGI)"]
        AuthMiddleware["JWT Authentication & RBAC Guard"]
        APIRouters["API Routers (/api/v1/*)"]
        ExceptionHandler["Normalized Global Exception Handler"]
    end

    subgraph DomainLayer ["Service & Business Logic Layer"]
        AuthService["Auth & Security Service (bcrypt)"]
        AvailEngine["5-Tier Dynamic Availability Engine"]
        ApptService["Appointment Lifecycle Service"]
        DeptService["Department & User Service"]
    end

    subgraph DataLayer ["Data Access & Storage Layer"]
        Repos["SQLAlchemy Repositories (Unit of Work)"]
        PostgresDB[("PostgreSQL Database<br/>(Row-Level FOR UPDATE Locks)")]
        Alembic["Alembic Migration Engine"]
    end

    StudentPortal -->|Axios HTTP/JSON + Bearer JWT| APILayer
    FacultyPortal -->|Axios HTTP/JSON + Bearer JWT| APILayer
    AdminPortal -->|Axios HTTP/JSON + Bearer JWT| APILayer

    APILayer --> AuthMiddleware
    AuthMiddleware --> APIRouters
    APIRouters --> DomainLayer

    DomainLayer --> Repos
    Repos --> PostgresDB
    Alembic -->|Schema Evolution| PostgresDB
```

---

## 2. 5-Tier Dynamic Availability Algebra

The platform uses interval algebra over continuous time intervals rather than static pre-allocated slots.

### The Canonical Precedence Formula:
$$\mathcal{A}_{\text{final}} = \Big( \big( \mathcal{R} \cup \mathcal{T} \big) \setminus \mathcal{B} \Big) \setminus \Big( \mathcal{L} \cup \mathcal{P} \cup \mathcal{C} \Big)$$

Where:
- $\mathcal{R}$: Regular recurring weekly office hours for the specified day-of-week.
- $\mathcal{T}$: Temporary/pop-up extra office hours scheduled for this specific calendar date.
- $\mathcal{B}$: Temporary blocked periods (busy periods, thesis defenses, conferences).
- $\mathcal{L}$: Approved faculty leave periods (`FULL_DAY`, `HALF_DAY_MORNING`, `HALF_DAY_AFTERNOON`, `MULTI_DAY`).
- $\mathcal{P}$: Pending/requested appointment reservations.
- $\mathcal{C}$: Confirmed/accepted scheduled appointments.

```mermaid
flowchart TD
    A["Base Availability: Union(Regular R, Temporary T)"] --> B["Apply Blocks: Subtract Blocked Periods B"]
    B --> C["Apply Leave: Subtract Approved Leave L"]
    C --> D["Apply Commitments: Subtract Appointments (P U C)"]
    D --> E["Time Filtering: Remove Past Intervals if Querying Today"]
    E --> F["Slot Generation: Partition Remaining Windows into 30-min Slots"]
```

---

## 3. Appointment Lifecycle & State Machine

```mermaid
stateDiagram-v2
    [*] --> REQUESTED: Student Books Free Slot
    
    REQUESTED --> ACCEPTED: Faculty Confirms (Optional Notes)
    REQUESTED --> REJECTED: Faculty Declines (Slot Released)
    REQUESTED --> CANCELLED: Student Cancels (Slot Released)
    
    ACCEPTED --> COMPLETED: Faculty Marks Done (Post Meeting)
    ACCEPTED --> CANCELLED: Student or Faculty Cancels (Slot Released)
    
    REJECTED --> [*]: Terminal State
    CANCELLED --> [*]: Terminal State
    COMPLETED --> [*]: Terminal State
```

### State Transition Rules:
1. **REQUESTED**:
   - `Accept` $\rightarrow$ transitions to `ACCEPTED`.
   - `Reject` $\rightarrow$ transitions to `REJECTED` and releases the time window back to the availability engine.
   - `Cancel` $\rightarrow$ transitions to `CANCELLED` and releases the slot.
2. **ACCEPTED**:
   - `Complete` $\rightarrow$ transitions to `COMPLETED` (validated against current IST time $\ge$ appointment end time).
   - `Cancel` $\rightarrow$ transitions to `CANCELLED` and frees the slot.
3. **Terminal States (`REJECTED`, `CANCELLED`, `COMPLETED`)**: No further state transitions allowed.

---

## 4. PostgreSQL Concurrency & Double-Booking Protection

To prevent race conditions where multiple students attempt to book the same 30-minute office hour slot simultaneously:

```mermaid
sequenceDiagram
    autonumber
    actor Student1 as Student 1 (Thread A)
    actor Student2 as Student 2 (Thread B)
    participant Engine as FastAPI Service
    participant DB as PostgreSQL Transaction

    Student1->>Engine: Book Slot (09:00 - 09:30)
    Student2->>Engine: Book Slot (09:00 - 09:30)
    
    Note over Engine,DB: Transaction A Begins
    Engine->>DB: SELECT * FROM faculty WHERE id = ? FOR UPDATE
    Note over DB: Lock Acquired by Transaction A

    Note over Engine,DB: Transaction B Waits on Row Lock
    Engine->>DB: SELECT * FROM faculty WHERE id = ? FOR UPDATE (BLOCKED)

    Engine->>DB: Calculate Real-Time Availability (09:00 is Available)
    Engine->>DB: INSERT INTO appointments (status = 'REQUESTED')
    Engine->>DB: COMMIT Transaction A
    Note over DB: Lock Released

    Note over DB: Transaction B Unblocks & Acquires Lock
    Engine->>DB: Calculate Real-Time Availability (09:00 is now Reserved!)
    Engine-->>Student2: 409 Conflict (SLOT_UNAVAILABLE)
    Engine->>DB: ROLLBACK Transaction B
    Engine-->>Student1: 201 Created (Appointment Booked)
```

---

## 5. Security & Authorization Matrix

| Endpoint Group | HTTP Method | Role Required | IDOR & Ownership Protection |
| :--- | :--- | :--- | :--- |
| `/api/v1/auth/*` | `POST`, `GET` | Public / Authenticated | JWT signature validation |
| `/api/v1/users/students/me` | `GET`, `PUT` | `STUDENT` | Modifies only token subject user profile |
| `/api/v1/users/faculty/me` | `GET`, `PUT` | `FACULTY` | Modifies only token subject faculty profile |
| `/api/v1/users/faculty` | `GET` | Authenticated | Public faculty discovery with department info |
| `/api/v1/admin/*` | `GET`, `POST`, `PATCH` | `ADMIN` | Strictly restricted to administrative accounts |
| `/api/v1/availability/regular` | `POST`, `PUT`, `DELETE` | `FACULTY` | Faculty can only modify their own hours |
| `/api/v1/availability/{id}` | `GET` | Authenticated | Privacy-preserving (hides internal leave notes) |
| `/api/v1/appointments` | `POST` | `STUDENT` | Validates target slot availability dynamically |
| `/api/v1/appointments/me` | `GET` | Authenticated | Role-filtered (Students see own; Faculty see own) |
| `/api/v1/appointments/{id}/accept` | `PUT` | `FACULTY` | Verified against assigned `faculty_id` |
| `/api/v1/appointments/{id}/cancel` | `PUT` | Authenticated | Permitted only to the appointment owner or admin |

---

## 6. Timezone Standard
- Institutional Base Timezone: `Asia/Kolkata` (IST, UTC+05:30).
- Storage Layer: Timestamps stored in UTC with timezone awareness.
- Presentation Layer: Slot calculations and UI displays operate consistently in IST, preventing timezone shift errors across distributed clients.
