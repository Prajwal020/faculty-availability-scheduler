# Project Showcase: Faculty Availability & Appointment Scheduler

A portfolio project showcase document summarizing the problem, solution, technical architecture, and engineering highlights for recruiters, hiring managers, and technical evaluators.

---

## 📌 Project Overview

- **Project Name**: Faculty Availability & Appointment Scheduler
- **GitHub Description**: Enterprise full-stack academic scheduling platform with dynamic 5-tier interval algebra, PostgreSQL concurrency protection, and role-based portals for Students, Faculty, and Administrators.
- **Technologies**: Python, FastAPI, PostgreSQL, SQLAlchemy 2.0, Alembic, React 18, TypeScript, Tailwind CSS, TanStack Query v5, Vitest, Pytest.
- **Short Summary**: A full-stack web application that eliminates email overhead and appointment race conditions in institutional environments by computing bookable faculty office hours in real time using continuous interval mathematics and serializing concurrent bookings with PostgreSQL row locks.

---

## 🎯 The Problem

In universities and research institutions:
1. **Unpredictable Schedules**: Faculty schedules change constantly due to academic conferences, grading periods, thesis defenses, and personal leave.
2. **Double Booking**: Popular office hours frequently receive simultaneous booking requests from multiple students, resulting in conflicting calendar events.
3. **Privacy & Communication Gaps**: Faculty need to block time for personal leaves without exposing confidential leave descriptions to the entire student body.

---

## 💡 The Solution

A role-based web application with real-time schedule calculation:
- **Zero Static Slot Generation**: Rather than creating millions of database rows for every 30-minute block in advance, availability is computed on-demand through interval set mathematics.
- **Concurrency-Safe Bookings**: PostgreSQL transactional row locks guarantee that no two students can ever book the same slot.
- **Dedicated Portals**: Role-specific user experiences for Students (search, dynamic slot selection, booking history), Faculty (recurring hours, pop-up hours, leaves, request reviews), and Administrators (user governance, department management).

---

## 🏗️ Technical Architecture Highlights

### 1. Dynamic Interval Algebra Calculation
The scheduling engine uses interval algebra over continuous time intervals:
$$\mathcal{A}_{\text{final}} = \Big( \big( \mathcal{R} \cup \mathcal{T} \big) \setminus \mathcal{B} \Big) \setminus \Big( \mathcal{L} \cup \mathcal{P} \cup \mathcal{C} \Big)$$
- $\mathcal{R}$: Regular recurring weekly hours.
- $\mathcal{T}$: Temporary pop-up office hours.
- $\mathcal{B}$: Temporary blocked periods.
- $\mathcal{L}$: Approved leaves.
- $\mathcal{P} \cup \mathcal{C}$: Existing pending or confirmed appointments.

### 2. Double-Booking Prevention with Row Locking
When a student requests a slot:
```sql
SELECT * FROM faculty WHERE id = :faculty_id FOR UPDATE;
```
This acquires an exclusive lock on the faculty member's row for the duration of the transaction. Even if 100 students click "Confirm Booking" at the exact same millisecond, only the first transaction succeeds; all others encounter a conflict check and safely receive `HTTP 409 Conflict (SLOT_UNAVAILABLE)` with automatic transaction rollback.

---

## 📸 Recommended Portfolio Screenshots

To capture for your portfolio website, resume links, or GitHub README:

1. **Authentication Screen (`/login`)**: Academic login card showing one-click demo selectors.
2. **Student Dashboard (`/student/dashboard`)**: Next scheduled appointment countdown and status cards.
3. **Faculty Directory (`/student/faculty`)**: Searchable card grid with department filters and meeting mode badges.
4. **Faculty Profile & Real-Time Availability (`/student/faculty/:id`)**: Dynamic 7-day quick date selector and calculated 30-minute slot buttons.
5. **Booking Modal (`BookingModal.tsx`)**: Modal with faculty details, slot summary, and agenda validation.
6. **Student Appointments List (`/student/appointments`)**: Tabbed status views (*All*, *Confirmed*, *Pending*, *Completed*, *Cancelled*).
7. **Faculty Dashboard (`/faculty/dashboard`)**: Pending requests banner and daily consultation schedule.
8. **Faculty Appointment Requests (`/faculty/requests`)**: Student details review with Accept/Reject workflow.
9. **Faculty Weekly Hours Manager (`/faculty/availability`)**: Day-by-day weekly recurring office hours table.
10. **Admin Governance Dashboard (`/admin/dashboard`)**: Total users, active accounts, and department distribution.
11. **Admin Faculty Management (`/admin/faculty`)**: Institutional faculty directory table.
12. **Admin User Management (`/admin/users`)**: User accounts table with 1-click status activation/suspension.

---

## 🧪 Test Matrix & Quality Verification

- **Backend Pytest**: 74 automated tests covering authentication, RBAC, IDOR isolation, availability algebra, slot generation, appointment lifecycle, and transaction rollback.
- **Frontend Vitest**: 20 unit and integration tests covering formatters, status badges, ErrorBoundary, RBAC guards, faculty management rendering, and booking modal conflict states.
- **TypeScript Production Build**: 0 errors, compiled in 2.97s.
