# Faculty Availability & Appointment Scheduler — Resume & Interview Guide

---

## 📌 One-Line Description
A full-stack institutional scheduling platform built with FastAPI, PostgreSQL, React, and TypeScript featuring a 5-tier dynamic continuous interval algebra engine and transactional row-level locking to eliminate appointment race conditions.

---

## 📄 3-Bullet Resume Version

- **Full-Stack Academic Scheduling Platform**: Architected a production-ready platform using **FastAPI**, **PostgreSQL**, **React 18**, **TypeScript**, and **TanStack Query**, providing dedicated role portals for Students, Faculty, and Administrators.
- **5-Tier Dynamic Interval Algebra Engine**: Designed and implemented real-time mathematical schedule calculation evaluating recurring weekly hours, pop-up availability, blocked periods, approved leaves, and pending appointments with zero static slot pre-allocation.
- **Concurrency & Concurrency-Safe Booking**: Enforced **PostgreSQL Row-Level Locking (`SELECT FOR UPDATE`)** and transactional rollback mechanisms, preventing race conditions during simultaneous booking attempts with 100% data integrity verified under automated multi-threaded tests.

---

## 🛠️ Technical Version (For Senior Engineering & Systems Roles)

- **Backend Architecture**: Built an asynchronous REST API using **FastAPI**, **SQLAlchemy 2.0**, **Alembic**, and **Pydantic v2** with normalized error handling, JWT Bearer authentication, salted bcrypt hashing, and server-side RBAC.
- **Interval Mathematics**: Implemented continuous time interval arithmetic ($[t_{\text{start}}, t_{\text{end}})$ set union, intersection, and difference) to compute available consultation windows dynamically across multiple precedence tiers.
- **Frontend State & Design**: Engineered a responsive React 18 client using **TypeScript (strict mode)**, **Vite**, **Tailwind CSS**, and **TanStack Query v5**, featuring optimistic UI updates, automated query cache invalidation, and custom Error Boundary / 404 recovery flows.
- **Automated Test Coverage**: Developed 74 backend tests (Pytest) and 20 frontend integration/unit tests (Vitest + Testing Library) covering authentication, state machine transitions, IDOR isolation, and thread-level double-booking prevention.

---

## 🎙️ Interview Talking Points

### 1. "Tell me about a challenging technical problem in this project."
> *"The hardest challenge was ensuring schedule accuracy without statically pre-generating calendar slots in the database. When faculty take leave or schedule one-time pop-up hours, statically pre-allocated slots become stale or require complex bulk updates. I solved this by treating availability as continuous mathematical intervals $[\text{start}, \text{end})$ and computing the exact available windows dynamically upon every request using interval set operations: regular weekly hours $\cup$ temporary hours $\setminus$ blocked periods $\setminus$ leaves $\setminus$ existing appointments."*

### 2. "How did you handle concurrent double bookings?"
> *"If two students attempt to book the same office hour slot at the exact same millisecond, standard application-level checks can suffer from read-then-write race conditions. I utilized PostgreSQL's `SELECT ... FOR UPDATE` row-level lock on the target Faculty record within a serial transaction. The first thread locks the record, computes availability, and commits the booking. The second thread unblocks, evaluates availability against the newly committed state, encounters a conflict, and triggers a clean rollback returning a `409 Conflict (SLOT_UNAVAILABLE)` response to the frontend."*

### 3. "How did you structure the frontend architecture?"
> *"I used React 18 with TypeScript, Vite, and TanStack Query v5. The frontend acts purely as a presentation and interaction layer without duplicating backend scheduling math. We used role-based route guards to enforce UX boundaries, while backend RBAC dependencies enforce actual security. On every appointment mutation (booking, accepting, rejecting, or cancelling), TanStack Query invalidates related query keys, keeping the client cache in instant sync with the database."*
