# Faculty Availability & Appointment Scheduler — API Specification

This document provides an overview of the REST API architecture, authentication model, error contracts, and primary endpoint groups. The backend is built with **FastAPI** and automatically publishes interactive OpenAPI documentation at `/docs` (Swagger UI) and `/redoc` (ReDoc).

---

## 1. Authentication & Security Model

The API uses **JWT Bearer Token Authentication (RFC 6750)**:
- **Header**: `Authorization: Bearer <access_token>`
- **Token Algorithm**: `HS256` (HMAC with SHA-256)
- **Token Expiry**: Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 24 hours / 1440 min)
- **Subject**: User ID (`UUID`)
- **Password Hashing**: `bcrypt` (salted, 12 rounds)

### Role-Based Access Control (RBAC)
- **`STUDENT`**: Self-service student profile management, public faculty discovery, real-time availability calculation, appointment booking, and personal appointment cancellation.
- **`FACULTY`**: Self-service faculty profile management, weekly recurring office hours CRUD, pop-up availability CRUD, blocked slots CRUD, leave declarations CRUD, appointment request review (accept/reject), schedule agenda, and appointment completion.
- **`ADMIN`**: Institutional governance, system user creation, user account status toggles (`ACTIVE` / `SUSPENDED` / `DEACTIVATED`), academic department CRUD, and system-wide appointment oversight.

---

## 2. Standard Error Response Envelope

All non-2xx responses follow a standardized JSON schema:

```json
{
  "error": {
    "code": "SLOT_UNAVAILABLE",
    "message": "The requested time slot is no longer available. Please select another time slot.",
    "details": {},
    "timestamp": "2026-08-15T12:00:00.000000Z"
  }
}
```

### Standard Error Codes:
- `UNAUTHORIZED` (401): Missing, expired, or invalid JWT token.
- `FORBIDDEN` (403): User role lacks required permission for this resource.
- `NOT_FOUND` (404): Target entity ID does not exist in the database.
- `SLOT_UNAVAILABLE` (409): Target appointment slot overlaps with existing booking, blocked period, or approved leave.
- `INVALID_TRANSITION` (409): Attempted state change violates appointment lifecycle (e.g. attempting to accept a cancelled appointment).
- `VALIDATION_ERROR` (422): Input parameters failed Pydantic schema validation.

---

## 3. Main API Endpoint Groups

### A. Authentication (`/api/v1/auth`)

| Method | Path | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login` | Public | Authenticate with email & password, returns JWT token & user summary. |
| `GET` | `/api/v1/auth/me` | Authenticated | Retrieve current authenticated user profile and roles. |
| `POST` | `/api/v1/auth/register/student` | Public | Register a new student account with student ID and academic major. |
| `POST` | `/api/v1/auth/register/faculty` | Public | Register a new faculty account with department ID and title. |

#### Example Login Request:
```http
POST /api/v1/auth/login HTTP/1.1
Content-Type: application/json

{
  "email": "prof.sharma@institution.edu",
  "password": "FacultyPassword123!"
}
```

#### Example Login Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "user": {
    "id": "eb1ff1c2-df86-451e-9185-dc59cef1324b",
    "email": "prof.sharma@institution.edu",
    "full_name": "Dr. Rajesh Sharma",
    "role": "FACULTY",
    "status": "ACTIVE",
    "faculty_profile": {
      "id": "3984faee-5336-4eb2-a5d4-bd79347a390b",
      "department_id": "1cb268e6-963c-452f-84ae-58100a72e33f",
      "employee_id_number": "FAC-1001",
      "title": "Professor & HOD",
      "office_location": "Turing Hall, Room 301",
      "meeting_mode": "HYBRID"
    }
  }
}
```

---

### B. Users & Profiles (`/api/v1/users`)

| Method | Path | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/users/students/me` | `STUDENT` | Get detailed student profile. |
| `PUT` | `/api/v1/users/students/me` | `STUDENT` | Update student major / details. |
| `GET` | `/api/v1/users/faculty/me` | `FACULTY` | Get detailed faculty profile. |
| `PUT` | `/api/v1/users/faculty/me` | `FACULTY` | Update faculty title, bio, office, meeting mode. |
| `GET` | `/api/v1/users/faculty` | Authenticated | List all active faculty with department information. |
| `GET` | `/api/v1/users/faculty/{faculty_id}` | Authenticated | Get public profile for a specific faculty member. |

---

### C. Departments (`/api/v1/departments`)

| Method | Path | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/departments` | Authenticated | List all active academic departments. |
| `GET` | `/api/v1/departments/{id}` | Authenticated | Get department details. |
| `POST` | `/api/v1/departments` | `ADMIN` | Create a new academic department. |
| `PUT` | `/api/v1/departments/{id}` | `ADMIN` | Update department name, code, or building. |

---

### D. Availability Engine (`/api/v1/availability`)

| Method | Path | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/availability/{faculty_id}` | Authenticated | Compute real-time dynamic bookable slots for a date. |
| `GET` | `/api/v1/availability/regular` | `FACULTY` | List recurring weekly availability windows. |
| `POST` | `/api/v1/availability/regular` | `FACULTY` | Create recurring weekly availability window (day: 0-6). |
| `PUT` | `/api/v1/availability/regular/{id}` | `FACULTY` | Update recurring availability window. |
| `DELETE` | `/api/v1/availability/regular/{id}`| `FACULTY` | Delete recurring availability window. |
| `GET` | `/api/v1/availability/temporary` | `FACULTY` | List temporary / pop-up extra availability windows. |
| `POST` | `/api/v1/availability/temporary` | `FACULTY` | Create pop-up availability window for specific date. |
| `DELETE` | `/api/v1/availability/temporary/{id}`| `FACULTY` | Delete pop-up availability window. |
| `GET` | `/api/v1/availability/blocked` | `FACULTY` | List temporary blocked busy periods. |
| `POST` | `/api/v1/availability/blocked` | `FACULTY` | Create temporary blocked busy period. |
| `DELETE` | `/api/v1/availability/blocked/{id}`| `FACULTY` | Remove blocked busy period. |

#### Example Dynamic Availability Calculation:
```http
GET /api/v1/availability/3984faee-5336-4eb2-a5d4-bd79347a390b?date=2026-08-24&duration=30 HTTP/1.1
Authorization: Bearer <token>
```

#### Example Dynamic Availability Response:
```json
{
  "faculty_id": "3984faee-5336-4eb2-a5d4-bd79347a390b",
  "date": "2026-08-24",
  "timezone": "Asia/Kolkata",
  "day_of_week": 0,
  "is_on_leave": false,
  "available_windows": [
    { "start_time": "09:30:00", "end_time": "12:00:00" },
    { "start_time": "14:00:00", "end_time": "16:00:00" }
  ],
  "slots": [
    {
      "start_datetime": "2026-08-24T09:30:00+05:30",
      "end_datetime": "2026-08-24T10:00:00+05:30",
      "start_time": "09:30",
      "end_time": "10:00",
      "duration_minutes": 30,
      "status": "AVAILABLE"
    },
    {
      "start_datetime": "2026-08-24T10:30:00+05:30",
      "end_datetime": "2026-08-24T11:00:00+05:30",
      "start_time": "10:30",
      "end_time": "11:00",
      "duration_minutes": 30,
      "status": "AVAILABLE"
    }
  ],
  "total_slots": 2,
  "leave_reason": null
}
```

---

### E. Leave Management (`/api/v1/leave`)

| Method | Path | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/leave` | `FACULTY` | List faculty's declared leave periods. |
| `POST` | `/api/v1/leave` | `FACULTY` | Submit leave declaration (`FULL_DAY`, `HALF_DAY_MORNING`, `HALF_DAY_AFTERNOON`, `MULTI_DAY`). |
| `DELETE` | `/api/v1/leave/{id}` | `FACULTY` | Cancel declared leave. |

---

### F. Appointments & Booking (`/api/v1/appointments`)

| Method | Path | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/appointments` | `STUDENT` | Book an appointment slot (serialized with row-level lock). |
| `GET` | `/api/v1/appointments/me` | Authenticated | List appointments for authenticated user (supports `status` and `date` filters). |
| `GET` | `/api/v1/appointments/{id}` | Authenticated | Get appointment details (student/faculty owner or admin). |
| `PUT` | `/api/v1/appointments/{id}/accept` | `FACULTY` | Accept a requested appointment with optional preparation notes. |
| `PUT` | `/api/v1/appointments/{id}/reject` | `FACULTY` | Reject a requested appointment with reason (releases slot). |
| `PUT` | `/api/v1/appointments/{id}/cancel` | Authenticated | Cancel appointment (owner or admin; releases slot). |
| `PUT` | `/api/v1/appointments/{id}/complete`| `FACULTY` / `ADMIN` | Mark accepted appointment as completed. |

#### Example Booking Request:
```http
POST /api/v1/appointments HTTP/1.1
Authorization: Bearer <student_token>
Content-Type: application/json

{
  "faculty_id": "3984faee-5336-4eb2-a5d4-bd79347a390b",
  "date": "2026-08-24",
  "start_time": "09:30:00",
  "end_time": "10:00:00",
  "reason": "Discuss capstone distributed consensus algorithm implementation"
}
```

---

### G. Admin Governance (`/api/v1/admin`)

| Method | Path | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/admin/users` | `ADMIN` | List all system users with attached profiles. |
| `POST` | `/api/v1/admin/users/create` | `ADMIN` | Create a new user with specified role and status. |
| `PATCH`| `/api/v1/admin/users/{user_id}/status`| `ADMIN` | Toggle user status (`ACTIVE`, `SUSPENDED`, `DEACTIVATED`). |
