# Faculty Availability & Appointment Scheduler — Live Demonstration Guide

A structured 2–3 minute walkthrough demonstration script showing the core workflows, role experiences, dynamic availability calculation, and PostgreSQL concurrency protection.

---

## ⏱️ Demonstration Timeline (2.5 Minutes)

### Phase 1: Student Discovery & Real-Time Slot Booking (45 seconds)
1. **Login as Student**:
   - Navigate to `http://localhost:5173/login`.
   - Click the **"Alex Rivera (Student)"** one-click demo button.
   - Click **Sign In**.
2. **Browse Faculty Directory**:
   - Navigate to `/student/faculty`.
   - Search for **"Sharma"** or filter by department **"Computer Science"**.
   - Click **"View Availability"** on **Dr. Rajesh Sharma**.
3. **Inspect Real-Time Calculated Slots**:
   - Notice the dynamic 7-day date selector. Select an available date (e.g. next Monday).
   - Observe available 30-minute consultation slots (e.g. `09:00 AM – 09:30 AM`).
4. **Book Appointment**:
   - Click a slot. In the booking modal, enter agenda: *"Discussion regarding distributed ML project draft"*.
   - Click **Confirm Request**.
   - Notice the status updates to `REQUESTED` and the slot is immediately removed from available options.

---

### Phase 2: Faculty Review & Approval Workflow (45 seconds)
1. **Switch to Faculty Session**:
   - Click the user avatar in the top right $\rightarrow$ **Sign Out**.
   - On the login page, click **"Dr. Rajesh Sharma (Faculty)"** demo button $\rightarrow$ **Sign In**.
2. **Review Appointment Requests**:
   - On the Faculty Dashboard (`/faculty/dashboard`), click **"Review Requests"** or navigate to `/faculty/requests`.
   - See the incoming request from Alex Rivera with his major, student ID, and requested agenda.
3. **Accept Request**:
   - Click **Accept**.
   - Enter optional faculty note: *"Please bring your preliminary latency benchmarks."*
   - Click **Confirm & Accept**.
4. **Inspect Faculty Schedule**:
   - Navigate to `/faculty/schedule` to see the confirmed appointment locked on the faculty agenda.

---

### Phase 3: Administrative Governance & Management (30 seconds)
1. **Switch to Admin Session**:
   - Sign Out $\rightarrow$ Click **"Admin (System Admin)"** demo button $\rightarrow$ **Sign In**.
2. **User & Faculty Oversight**:
   - Open `/admin/dashboard` to view institutional metrics (total users, active accounts, department distribution).
   - Open `/admin/faculty` to inspect all faculty profiles and departmental allocations.
   - Open `/admin/users` to demonstrate 1-click user account status toggles (`ACTIVE` $\leftrightarrow$ `SUSPENDED`).

---

### Phase 4: The Technical Highlight — PostgreSQL Concurrency Protection (30 seconds)

#### The Scenario:
Two students attempt to book the exact same 30-minute office hour slot simultaneously.

```
Student 1 (Thread A) ───► POST /appointments (09:00 - 09:30) ───┐
                                                                ├─► PostgreSQL FOR UPDATE Lock
Student 2 (Thread B) ───► POST /appointments (09:00 - 09:30) ───┘
```

#### The Result:
1. **Thread A** acquires the row lock on the faculty member, verifies slot availability, inserts the appointment, and commits the transaction (`201 Created`).
2. **Thread B** unblocks, re-evaluates the availability engine against the committed database state, detects the overlap conflict, rolls back the transaction, and returns:
   ```json
   HTTP/1.1 409 Conflict
   {
     "error": {
       "code": "SLOT_UNAVAILABLE",
       "message": "The requested time slot is no longer available. Please select another time slot."
     }
   }
   ```
3. The UI in Student 2's session displays: *"This slot was just booked or is no longer available. Please select another time slot."*
4. The database retains exactly **1** appointment, completely eliminating race conditions.
