# Phase 0: Requirements & Business Rules Specification
## System Name: Faculty Availability & Appointment Scheduler

---

## 1. PRODUCT DEFINITION

The **Faculty Availability & Appointment Scheduler** is a web-based enterprise scheduling platform built specifically for higher education institutions. Its primary purpose is to eliminate the friction, communication overhead, and scheduling ambiguity between students and faculty members by providing a real-time, dynamic calculation of faculty availability and facilitating a structured appointment lifecycle.

Unlike static meeting booking applications (e.g., standard Calendly or generic calendar tools) that rely on fixed weekly timetables or simple calendar free/busy slots, this platform operates on a multi-layered **Dynamic Availability Engine**. Higher education environments are inherently fluid: faculty members balance lectures, research labs, impromptu administrative meetings, last-minute class cancellations, unscheduled student consultations, and official leaves. Standard static calendars quickly become out of date, leading to frustrated students, missed meetings, double-booking, and incessant email back-and-forth.

The system serves three primary user cohorts: **Students**, **Faculty Members**, and **Institutional Administrators**. For students, it delivers transparent, up-to-the-minute visibility into when a faculty member is truly free to meet and enables instant appointment requests. For faculty, it offers granular control over recurring office hours, one-time temporary availability windows (e.g., "free for the next 45 minutes following a cancelled lecture"), temporary block periods, and leave declarations. For administrators, it provides central governance, departmental management, policy enforcement, and auditability across all academic interactions.

---

## 2. PROBLEM STATEMENT

In traditional university and college environments, determining when a professor or lecturer is available to consult with a student is remarkably inefficient. The core challenges include:

1. **Failure of Static Timetables:** Official semester timetables show fixed teaching hours but fail to capture administrative duties, research group meetings, unexpected department calls, or spontaneous advisory sessions. A professor listed as "free" on paper is frequently occupied with unannounced tasks.
2. **Unused Spontaneous Free Windows:** When a lecture or lab is cancelled unexpectedly, faculty members often have open time windows where they could assist students. However, without a real-time publishing mechanism, students remain unaware of these opportunities.
3. **High Communication Friction & "Phone Tag":** Students repeatedly visit faculty offices unannounced—only to find locked doors—or send endless emails asking "When are you free?" This causes severe delay in urgent academic guidance, thesis reviews, and project evaluations.
4. **Double Bookings & Schedule Clashes:** Manual appointment scheduling via email or chat often leads to multiple students being promised the same time slot, creating embarrassment and schedule collisions.
5. **Impact of Leaves & Absences:** When faculty members take full-day or half-day leave, existing student appointments are frequently forgotten or cancelled without timely, automated notifications.
6. **Lack of Institutional Visibility:** Department heads and campus administrators lack centralized visibility into faculty advisory workloads, student engagement metrics, or auditable appointment logs.

**Conclusion:** A static weekly schedule is fundamentally insufficient for modern academic workflows. What is required is a **dynamic scheduling engine** that computes real-time availability by overlaying regular schedules, temporary availability, temporary blocks, approved leave, and existing appointments under strict mathematical precedence rules.

---

## 3. GOALS

### Primary Goals

1. **Dynamic Availability Engine:** Compute true, real-time bookable slots in under 200 milliseconds by evaluating regular office hours, temporary availability, temporary blocks, leave records, and existing appointments.
2. **Elimination of Double-Bookings:** Guarantee zero concurrent or overlapping accepted appointments for any faculty member via strict transactional and concurrency controls (`FR-CON-001`).
3. **Real-time Temporary Window Publishing:** Enable faculty to instantly declare spontaneous temporary availability (e.g., 30-minute pop-up slots) that immediately become visible and bookable for students.
4. **Structured Lifecycle Management:** Enforce a deterministic state machine for appointment requests (`REQUESTED` $\rightarrow$ `ACCEPTED` / `REJECTED` / `RESCHEDULE_PROPOSED` $\rightarrow$ `COMPLETED` / `CANCELLED` / `NO_SHOW`).
5. **Self-Service Student Discovery:** Allow students to search, filter, view dynamic calendar slots, and submit appointment requests in 3 clicks or fewer.
6. **Auditable System History:** Maintain immutable audit logs for all appointment state transitions, cancellations, leave applications, and admin policy overrides.

### Secondary Goals

1. **Email & Communication Reduction:** Decrease scheduling-related email exchanges between students and faculty by at least 85%.
2. **Departmental Analytics:** Provide department heads and administrators with aggregated insights regarding consultation volume, peak demand times, and response rates.
3. **Extensible Architecture:** Establish clean domain boundaries to seamlessly support future integrations (e.g., Google/Outlook calendar sync, email/SMS gateways, WebSockets).

---

## 4. NON-GOALS

To maintain strict focus and deliver a robust MVP, the following items are explicitly categorized as **Non-Goals** for the initial system release:

1. **Academic Semester Timetable Generation:** The system will NOT generate master class schedules, classroom allocations, or semester course timetables.
2. **Classroom & Facility Reservation:** The system will NOT manage room keys, lab equipment, or physical facility bookings.
3. **Exam & Invigilation Scheduling:** The system will NOT schedule midterms, final examinations, or proctoring rosters.
4. **Payroll & HR Management:** The system will NOT calculate faculty salaries, hourly leave pay, or formal employment benefits.
5. **Student Attendance Tracking:** The system will NOT record or report lecture/lab attendance.
6. **Full Institutional ERP Capabilities:** The system will NOT replace existing Student Information Systems (SIS) or Learning Management Systems (LMS) like Canvas or Blackboard.

---

## 5. USER ROLES & PERMISSIONS MATRIX

The system defines three core roles with distinct permissions:

```
                  ┌──────────────────────────────────────────┐
                  │                 ADMIN                    │
                  │ (Full Governance, Policy & User Config)  │
                  └────────────────────┬─────────────────────┘
                                       │
           ┌───────────────────────────┴───────────────────────────┐
           ▼                                                       ▼
┌─────────────────────────────────────┐         ┌─────────────────────────────────────┐
│               FACULTY               │         │               STUDENT               │
│ (Schedule, Temp Slots, Approval)    │         │ (Search, Request, Cancel, Reschedule)│
└─────────────────────────────────────┘         └─────────────────────────────────────┘
```

### Detailed Role Capabilities

| Feature / Action | Student | Faculty | Admin |
| :--- | :---: | :---: | :---: |
| **Account Login / Logout** | Yes | Yes | Yes |
| **Manage Personal Profile** | Yes (Basic) | Yes (Bio, Office, Specs) | Yes (Any User) |
| **Search & View Faculty Profiles** | Yes | Yes | Yes |
| **View Faculty Dynamic Availability** | Yes | Yes | Yes |
| **Define Recurring Weekly Availability** | No | Yes | Yes (On behalf) |
| **Publish Temporary Availability** | No | Yes | No |
| **Publish Temporary Block / Unavailability** | No | Yes | Yes |
| **Mark / Request Leave** | No | Yes | Yes |
| **Submit Appointment Request** | Yes | No | No |
| **Accept / Reject Appointment Request** | No | Yes | No |
| **Propose Reschedule** | No | Yes | No |
| **Accept / Reject Reschedule Proposal** | Yes | No | No |
| **Cancel Appointment** | Yes (Own) | Yes (Own) | Yes (Any) |
| **Mark Appointment Completed / No-Show** | No | Yes | Yes |
| **View Appointment History** | Yes (Own) | Yes (Own) | Yes (System-wide) |
| **System-wide Policy Configuration** | No | No | Yes |
| **Department & User Management** | No | No | Yes |
| **View Operational Analytics** | No | No | Yes |

---

## 6. FUNCTIONAL REQUIREMENTS

### Authentication & Access Control

* **FR-AUTH-001:** The system shall allow users (Students, Faculty, Admins) to log in using institutional email credentials and a secure password.
* **FR-AUTH-002:** The system shall issue secure JWT tokens / session identifiers upon successful authentication.
* **FR-AUTH-003:** The system shall enforce Role-Based Access Control (RBAC) on all protected API endpoints and UI routes.
* **FR-AUTH-004:** The system shall automatically invalidate user sessions upon explicit logout or token expiration.

### User & Profile Management

* **FR-USR-001:** The system shall maintain user records containing `user_id`, `full_name`, `email`, `role`, `department_id`, and `account_status` (Active / Suspended / Deactivated).
* **FR-USR-002:** The system shall allow Faculty members to maintain a public profile including office location, bio, areas of expertise, and preferred meeting mode (In-person / Virtual link).
* **FR-USR-003:** The system shall allow Students to view their own profile and update contact preferences.

### Faculty Search & Discovery

* **FR-SCH-001:** The system shall allow students to search for faculty members by name, department, expertise, or research area.
* **FR-SCH-002:** The system shall allow filtering of search results by current day availability or department.
* **FR-SCH-003:** The system shall render a detailed profile view for each faculty member displaying bio, office details, and calculated dynamic availability slots.

### Regular Weekly Availability

* **FR-REG-001:** The system shall allow faculty members to define recurring weekly availability rules (e.g., Mondays 09:00–12:00, Wednesdays 14:00–17:00).
* **FR-REG-002:** The system shall support multiple distinct time windows per day for regular availability.
* **FR-REG-003:** The system shall allow faculty members to modify or delete recurring availability rules. Changes shall apply to future unbooked dates without corrupting past historical records.

### Temporary Availability

* **FR-TAV-001:** The system shall allow faculty members to publish one-time, short-term temporary availability windows specifying a start date/time and end date/time.
* **FR-TAV-002:** The system shall make published temporary availability immediately visible and bookable for students.
* **FR-TAV-003:** The system shall automatically expire and unpublish temporary availability slots once the current system time exceeds the configured end time.
* **FR-TAV-004:** The system shall allow faculty to edit or delete unbooked temporary availability entries.

### Temporary Unavailability / Blocking

* **FR-BLK-001:** The system shall allow faculty members to define one-time temporary blocked periods (start date/time, end date/time, reason).
* **FR-BLK-002:** The system shall subtract temporary blocked periods from regular availability when calculating bookable slots.
* **FR-BLK-003:** The system shall alert faculty if a newly posted temporary block overlaps with existing accepted or pending student appointments, prompting a resolution action (cancellation or rescheduling).

### Leave Management

* **FR-LVE-001:** The system shall allow faculty to submit leave entries categorized as Full-Day, Half-Day Morning (08:00–13:00), Half-Day Afternoon (13:00–18:00), or Multi-Day.
* **FR-LVE-002:** The system shall automatically negate all regular and temporary availability for the duration of approved leave.
* **FR-LVE-003:** The system shall automatically trigger cancellation or reschedule notifications for any existing appointments falling within an approved leave period (`FR-LVE-004`).

### Dynamic Slot Generation Engine

* **FR-SLT-001:** The system shall dynamically compute bookable slots for any requested date range by evaluating the Availability Precedence Model (`Section 8`).
* **FR-SLT-002:** The system shall slice continuous available time windows into discrete slots based on institutionally or faculty-configured slot durations (e.g., 15, 30, or 60 minutes).
* **FR-SLT-003:** The system shall enforce a minimum advance notice window (e.g., 2 hours prior to slot start) preventing instant impulse bookings.
* **FR-SLT-004:** The system shall enforce a maximum booking horizon (e.g., 14 calendar days in advance).

### Appointment Requests & Workflow

* **FR-APT-001:** The system shall allow students to select an available generated slot and submit an appointment request accompanied by a mandatory purpose/agenda statement.
* **FR-APT-002:** The system shall create the appointment in `REQUESTED` state and place a temporary pending lock on the slot (`FR-APT-003`).
* **FR-APT-003:** The system shall prevent other students from booking a slot that currently has an active `REQUESTED` or `ACCEPTED` status.
* **FR-APT-004:** The system shall allow faculty to `ACCEPT` or `REJECT` a pending appointment request. Rejections shall require a brief explanation.
* **FR-APT-005:** The system shall allow faculty to mark an accepted past appointment as `COMPLETED` or `NO_SHOW`.

### Rescheduling Workflow

* **FR-RSC-001:** The system shall allow faculty to propose an alternative slot for a pending or accepted appointment, transitioning the state to `RESCHEDULE_PROPOSED`.
* **FR-RSC-002:** The system shall hold the proposed new slot in tentative state while releasing or soft-locking the original slot according to policy (`Section 17`).
* **FR-RSC-003:** The system shall allow the student to accept or decline the reschedule proposal. If accepted, the state transitions to `ACCEPTED` at the new time. If declined, the appointment is `CANCELLED`.

### Cancellation Workflow

* **FR-CAN-001:** The system shall allow students to cancel pending or accepted appointments up to a configured cancellation deadline (e.g., 1 hour before start).
* **FR-CAN-002:** The system shall allow faculty members to cancel any appointment prior to the start time with a mandatory cancellation reason.
* **FR-CAN-003:** Upon cancellation, the system shall transition the appointment to `CANCELLED` and immediately release the associated slot back into the bookable pool (if still within valid future booking parameters).

### Notifications Engine

* **FR-NTF-001:** The system shall generate real-time in-app notifications for users upon any status transition of their appointments (Request, Accept, Reject, Reschedule, Cancel).
* **FR-NTF-002:** The system shall maintain an unread notification counter and persistent notification history for each user.

### Admin Configuration & Governance

* **FR-ADM-001:** The system shall allow administrators to create, update, suspend, or deactivate user accounts (Students and Faculty).
* **FR-ADM-002:** The system shall allow administrators to manage departments and assign faculty to departments.
* **FR-ADM-003:** The system shall allow administrators to configure global scheduling parameters: Default Slot Duration, Min Advance Notice, Max Booking Horizon, Max Pending Requests per Student.
* **FR-ADM-004:** The system shall provide administrators with basic aggregate analytics: total appointments created, acceptance rate, cancellation rate, and department consultation totals.

---

## 7. AVAILABILITY MODEL

The core of the system is the **Dynamic Availability Engine**. Availability is not stored as fixed slot rows in a database; instead, available time intervals are **calculated on-the-fly** whenever requested by a user.

### Set-Based Mathematical Formulation

Let $T$ represent the continuous time domain for a given date. The final set of Bookable Free Intervals $\mathcal{A}_{\text{final}}$ for a faculty member is calculated as:

$$\mathcal{A}_{\text{final}} = \Big( \big( \mathcal{R} \setminus \mathcal{B} \big) \cup \mathcal{T} \Big) \setminus \Big( \mathcal{L} \cup \mathcal{P} \cup \mathcal{C} \Big)$$

Where:
* $\mathcal{R}$ = Set of recurring **Regular Availability** intervals for the given day of the week.
* $\mathcal{B}$ = Set of **Temporary Block** / Unavailability intervals.
* $\mathcal{T}$ = Set of published **Temporary Availability** intervals.
* $\mathcal{L}$ = Set of approved **Leave** intervals (Full-day or Half-day).
* $\mathcal{P}$ = Set of time intervals occupied by **Pending (`REQUESTED`) Appointments**.
* $\mathcal{C}$ = Set of time intervals occupied by **Confirmed (`ACCEPTED`) Appointments**.

### Concrete Example Walkthrough

Consider a Faculty Member on a given Monday:

* **Regular Schedule ($\mathcal{R}$):** `09:00 - 12:00` and `14:00 - 17:00`
* **Temporary Block ($\mathcal{B}$):** `10:30 - 11:30` (Department meeting)
* **Temporary Availability ($\mathcal{T}$):** `12:15 - 12:45` (Pop-up office hour after cancelled lecture)
* **Leave ($\mathcal{L}$):** None (`00:00 - 00:00`)
* **Accepted Appointment ($\mathcal{C}$):** `09:30 - 10:00`
* **Pending Request ($\mathcal{P}$):** `15:00 - 15:30`

**Step-by-Step Calculation:**
1. Base Regular Hours: $[09:00, 12:00) \cup [14:00, 17:00)$
2. Subtract Temp Block ($[10:30, 11:30)$):
   $\rightarrow [09:00, 10:30) \cup [11:30, 12:00) \cup [14:00, 17:00)$
3. Union Temp Availability ($[12:15, 12:45)$):
   $\rightarrow [09:00, 10:30) \cup [11:30, 12:00) \cup [12:15, 12:45) \cup [14:00, 17:00)$
4. Subtract Leave (None): No change.
5. Subtract Existing Appointments ($[09:30, 10:00)$ and $[15:00, 15:30)$):
   $\rightarrow [09:00, 09:30) \cup [10:00, 10:30) \cup [11:30, 12:00) \cup [12:15, 12:45) \cup [14:00, 15:00) \cup [15:30, 17:00)$

The Slot Generation Engine then divides these remaining free continuous intervals into discrete bookable slots (e.g., 30-minute blocks).

---

## 8. AVAILABILITY PRECEDENCE HIERARCHY

To avoid ambiguity when different schedule directives overlap, the system enforces a strict 5-tier Precedence Hierarchy:

```
┌──────────────────────────────────────────────────────────┐
│ Tier 1: Existing Accepted / Pending Appointments         │ (HIGHEST)
├──────────────────────────────────────────────────────────┤
│ Tier 2: Approved Leave (Full-day / Half-day)             │
├──────────────────────────────────────────────────────────┤
│ Tier 3: Temporary Block / Unavailability                 │
├──────────────────────────────────────────────────────────┤
│ Tier 4: Temporary Availability (Pop-up Slots)            │
├──────────────────────────────────────────────────────────┤
│ Tier 5: Regular Weekly Availability (Base Schedule)      │ (LOWEST)
└──────────────────────────────────────────────────────────┘
```

### Precedence Resolution Rules

1. **Appointments Over Everything:** An accepted or pending appointment locks out the slot. Neither a new temporary block, new regular schedule, nor new temporary availability can silently erase an active appointment. (Leave triggers explicit cancellation flows; see `Section 11`).
2. **Leave Over Availability:** Approved Leave completely negates Regular Availability (Tier 5) and Temporary Availability (Tier 4).
   * *Explicit Policy Decision on Overrides:* Can faculty publish Temporary Availability on a day marked as Leave? **NO.** Leave indicates official absence from campus/duty. If a faculty member wishes to meet students, they must first edit or cancel the leave record. This prevents contradictory administrative records.
3. **Temporary Block Over Regular Availability:** A Temporary Block (Tier 3) overrides Regular Availability (Tier 5).
4. **Temporary Block Over Temporary Availability:** If a faculty member posts a Temporary Availability window (`11:00-12:00`) and subsequently posts a Temporary Block (`11:30-12:00`), the Temporary Block wins for the overlapping segment (`11:30-12:00`).

---

## 9. TEMPORARY AVAILABILITY RULES

Temporary Availability enables "pop-up" office hours.

### Conceptual Model: Published vs. Booked Availability

* **Published Temporary Availability:** The raw time window published by faculty (e.g., Today `11:15` to `11:45`).
* **Booked Availability:** The subset of published temporary availability that has been converted into a `REQUESTED` or `ACCEPTED` appointment by a student.

### Lifecycle & Operational Rules

1. **Parameters:** Faculty must define `start_datetime` and `end_datetime`.
2. **Minimum / Maximum Duration:** Minimum duration is equal to single slot duration (15 mins); maximum duration is 8 hours.
3. **Immediate Visibility:** Upon creation, published temporary availability is immediately evaluated by the engine and exposed to searching students.
4. **Automatic Expiration:** Once `current_datetime > end_datetime`, any remaining unbooked slots automatically vanish from student view. No background cleanup job is required because slot generation filtering naturally excludes past slots (`start_datetime < current_time + min_lead_notice`).
5. **Editing & Deletion:**
   * Faculty may edit or delete a temporary availability entry **only if no student has booked a slot** within that window.
   * If a slot within the window is already booked (`REQUESTED` or `ACCEPTED`), deletion of the temporary availability window is restricted; the faculty must cancel the specific appointment first.
6. **Overlap with Regular Schedule:** If temporary availability overlaps with regular weekly availability, the engine merges the intervals seamlessly without producing duplicate slots.

---

## 10. TEMPORARY UNAVAILABILITY (BLOCKING) RULES

Temporary Unavailability allows faculty to block off normally open regular office hours.

### Operational Rules

1. **Parameters:** Faculty must define `start_datetime`, `end_datetime`, and a mandatory `reason` (e.g., "Department Meeting", "Research Deadline", "Personal Emergency").
2. **Subtraction Logic:** The specified interval is strictly subtracted from Tier 5 (Regular) and Tier 4 (Temp Availability) schedules.
3. **Impact on Existing Appointments:**
   * If a temporary block is created over a period with **no existing appointments**, the block is posted silently and slots disappear immediately.
   * If a temporary block overlaps with **existing pending or accepted appointments**, the system blocks creation until the faculty chooses one of two resolution modes:
     * **Mode A (Auto-Cancel):** System cancels overlapping appointments, sends cancellation notices with the block reason to students, and posts the block.
     * **Mode B (Reschedule Prompt):** System places overlapping appointments into `RESCHEDULE_PROPOSED` mode and posts the block.

---

## 11. LEAVE RULES

Leave represents formal absence from institutional duties.

### Types of Leave

1. **Full-Day Leave:** Covers `00:00:00` to `23:59:59` of the specified date.
2. **Half-Day Morning Leave:** Covers `08:00:00` to `13:00:00`.
3. **Half-Day Afternoon Leave:** Covers `13:00:00` to `18:00:00`.
4. **Multi-Day Leave:** Spans across multiple consecutive calendar dates.

### Governance & Workflow

1. **Self-Declaration vs. Admin Approval:**
   * *MVP Rule:* Faculty members can self-declare leave directly in the system for scheduling purposes. Administrators receive a log notification and retain override/deletion authority.
2. **Impact on Existing Appointments:**
   * When leave is saved, all overlapping `REQUESTED` and `ACCEPTED` appointments are **automatically transitioned to `CANCELLED`** (with reason: *"Faculty on Official Leave"*).
   * Affected students receive high-priority in-app notifications.
3. **Visibility:** The faculty profile remains searchable, but calendar slot generation returns **zero bookable slots** for the leave duration. A clear banner ("Faculty on Leave") is displayed on the profile calendar for those dates.

---

## 12. APPOINTMENT MODEL & LIFECYCLE STATE MACHINE

An appointment follows a deterministic finite state machine.

### State Diagram

```
                 [ Student Requests Slot ]
                             │
                             ▼
                        ┌──────────┐
                        │REQUESTED │
                        └────┬─────┘
                             │
       ┌─────────────────────┼─────────────────────┐
       │ (Faculty Accepts)   │ (Faculty Rejects)   │ (Faculty Proposes
       ▼                     ▼                     │  Reschedule)
┌──────────┐            ┌──────────┐               ▼
│ ACCEPTED │            │ REJECTED │     ┌────────────────────┐
└────┬─────┘            └──────────┘     │RESCHEDULE_PROPOSED │
     │                                   └─────────┬──────────┘
     ├──────────────────────┐                      │
     │ (Faculty/Student     │ (Faculty Marks       ├─────────────────────┐
     │  Cancels)            │  Completion)         │ (Student Accepts)   │ (Student Declines)
     ▼                      ▼                      ▼                     ▼
┌──────────┐           ┌──────────┐           ┌──────────┐          ┌──────────┐
│CANCELLED │           │COMPLETED │           │ ACCEPTED │          │CANCELLED │
└──────────┘           └──────────┘           └──────────┘          └──────────┘
                            │
                            │ (Faculty Marks No-Show)
                            ▼
                       ┌──────────┐
                       │ NO_SHOW  │
                       └──────────┘
```

### State Definitions

* **`REQUESTED`:** Initial state upon student submission. Slot is reserved pending faculty action.
* **`ACCEPTED`:** Faculty has confirmed the appointment. Slot is locked.
* **`REJECTED`:** Faculty has declined the request with a reason. Slot is released.
* **`RESCHEDULE_PROPOSED`:** Faculty suggested a new time. Proposed slot is held; original slot is handled per rescheduling rules.
* **`CANCELLED`:** Appointment terminated by student, faculty, or admin prior to completion. Slot is released.
* **`COMPLETED`:** Faculty marked the meeting as successfully conducted post-meeting time.
* **`NO_SHOW`:** Faculty marked that the student failed to attend the accepted meeting.

---

## 13. BOOKING RULES & SYSTEM DEFAULTS

To ensure fair access and prevent system abuse, the following booking rules are enforced:

### Configurable System Parameters & MVP Defaults

| Parameter | MVP Default Value | Description |
| :--- | :--- | :--- |
| **Default Slot Duration** | 30 minutes | Standard appointment interval. |
| **Allowed Slot Durations** | 15, 30, 60 minutes | Options selectable by faculty. |
| **Min Advance Notice (Lead Time)** | 2 hours | Minimum lead time before slot start time. |
| **Max Advance Booking Horizon** | 14 calendar days | How far into the future students can book. |
| **Same-Day Booking** | Allowed | Permitted if notice $\ge$ Min Advance Notice. |
| **Max Active Requests / Student** | 3 active requests | Max concurrent `REQUESTED` items per student. |
| **Max Bookings / Student / Faculty / Day** | 1 booking | Prevents a single student from hoarding a professor's entire day. |
| **Pending Slot Locking** | Enabled | `REQUESTED` appointments reserve the slot immediately. |
| **Pending Request Auto-Expiration** | 24 hours (or 2h before slot) | Unresponded requests auto-cancel if ignored. |

---

## 14. CONFLICT RULES & INTERVAL MATHEMATICS

### Overlap Definition

Two time intervals $A = [A_{\text{start}}, A_{\text{end}})$ and $B = [B_{\text{start}}, B_{\text{end}})$ present a **Conflict (Overlap)** if and only if:

$$\max(A_{\text{start}}, B_{\text{start}}) < \min(A_{\text{end}}, B_{\text{end}})$$

### Boundary Contact Rule

If $A_{\text{end}} = B_{\text{start}}$, the intervals touch at a boundary point. This is **strictly NOT a conflict**.

* *Example:* Slot 1 (`10:00 - 10:30`) and Slot 2 (`10:30 - 11:00`) can be booked consecutively without conflict.

### Evaluation Matrix

| Existing State | Proposed New Entity | Evaluation Result |
| :--- | :--- | :--- |
| `ACCEPTED` Appointment | New Booking Request | **CONFLICT** (Rejected) |
| `REQUESTED` (Pending) | New Booking Request | **CONFLICT** (Rejected) |
| Approved Leave | New Booking Request | **CONFLICT** (Rejected) |
| Temporary Block | New Booking Request | **CONFLICT** (Rejected) |
| Published Temp Avail | New Temp Block | Block overrides overlapping portion. |
| `ACCEPTED` Appointment | New Temp Block | Block creation halted until conflict resolved. |

---

## 15. CONCURRENCY & ATOMICITY REQUIREMENTS

A critical requirement of the system is absolute prevention of double-bookings under race conditions.

* **FR-CON-001 (Atomic Reservation Requirement):** The system shall guarantee that under simultaneous booking attempts by multiple students for the exact same slot $[T_{\text{start}}, T_{\text{end}})$, exactly **one** booking request succeeds, while all concurrent attempts fail cleanly.
* **Concurrency Failure Response:** Secondary request attempts must receive a structured `409 Conflict` HTTP response with error code `SLOT_NO_LONGER_AVAILABLE` and an immediate refresh of bookable slots.
* **Mechanism Constraint (Phase 0 Requirement):** The booking process must be engineered using strict database transaction isolation (e.g., `SERIALIZABLE` or `SELECT FOR UPDATE` pessimistic row locking) or unique slot constraint indexes to ensure atomicity.

---

## 16. CANCELLATION RULES

1. **Student Cancellations:**
   * Students may cancel `REQUESTED` or `ACCEPTED` appointments up to **1 hour prior** to slot start time.
   * Reason is optional for students.
   * Late cancellation (< 1 hour) is disabled for students in MVP to protect faculty schedules.
2. **Faculty Cancellations:**
   * Faculty members may cancel an appointment at **any time** prior to or during the scheduled slot.
   * Reason is mandatory for faculty.
3. **Admin Cancellations:**
   * Administrators retain authority to cancel any appointment at any time for administrative reasons.
4. **Post-Cancellation Slot Lifecycle:**
   * When an appointment is cancelled, the underlying time slot is immediately returned to the pool of calculated available availability, provided the slot start time is still in the future and satisfies minimum lead time rules.

---

## 17. RESCHEDULING RULES

Rescheduling is designed as a clean, asymmetric flow initiated by Faculty and accepted/declined by Students.

1. **Initiation:** Faculty selects an existing appointment ($A_{\text{old}}$) and chooses a new target available slot ($A_{\text{new}}$).
2. **State Transition:** Appointment state changes to `RESCHEDULE_PROPOSED`.
3. **Slot Reservation Strategy:**
   * The proposed slot $A_{\text{new}}$ is immediately soft-locked for the target student (preventing other students from booking it).
   * The original slot $A_{\text{old}}$ is released back to the general available pool so other students can utilize it.
4. **Student Response Window:**
   * The student has 24 hours (or until 2 hours before $A_{\text{new}}$ start time) to respond.
   * **If Accepted:** Appointment moves to `ACCEPTED` at time $A_{\text{new}}$.
   * **If Declined or Expired:** Appointment moves to `CANCELLED`. $A_{\text{new}}$ soft-lock is released.

---

## 18. NOTIFICATION REQUIREMENTS

The MVP relies on **In-App Real-Time Notifications** (Notification Bell / Dashboard Feed).

| Event | Target Recipient | Priority | Message Content Summary |
| :--- | :--- | :--- | :--- |
| **New Appointment Request** | Faculty | High | Student X requested appointment for [Date, Time]. |
| **Request Accepted** | Student | High | Prof Y accepted your appointment request for [Date, Time]. |
| **Request Rejected** | Student | Normal | Prof Y was unable to accept your request. Reason: [Reason]. |
| **Reschedule Proposed** | Student | High | Prof Y proposed moving your meeting to [New Date, Time]. |
| **Appointment Cancelled** | Opposite Party | High | [User] cancelled the appointment scheduled for [Date, Time]. |
| **Leave Marked** | Affected Students | High | Prof Y marked leave. Your appointment on [Date] has been cancelled. |
| **2-Hour Reminder** | Both | Normal | Reminder: Upcoming appointment with [User] in 2 hours. |

---

## 19. ADMIN REQUIREMENTS & SYSTEM GOVERNANCE

Administrators oversee institutional compliance and system configuration.

1. **User Account Governance:** Ability to onboard users in bulk, edit profiles, reset credentials, and suspend/deactivate accounts.
2. **Departmental Management:** Define institutional faculties/departments (e.g., Computer Science, Mechanical Engineering) and assign department heads.
3. **Global System Controls:**
   * Modify system-wide scheduling parameters (Slot duration, Min notice, Max horizon).
   * Define official institutional holidays (which act as system-wide leave days).
4. **Audit Trail Inspection:** Search and view logs of all state changes, cancellations, and user logins.
5. **Basic System Analytics:** Display dashboard metrics:
   * Total appointments requested vs accepted.
   * Faculty response time distribution.
   * Peak requested hours by department.

---

## 20. NON-FUNCTIONAL REQUIREMENTS

### Performance
* **NFR-PERF-001:** Slot calculation query latency shall not exceed **200 milliseconds** for a standard 14-day horizon request under expected load.
* **NFR-PERF-002:** Page load times for search and profile views shall be under **1.2 seconds**.

### Availability & Reliability
* **NFR-AVL-001:** System uptime shall be **99.9%** during core operational academic hours (07:00 to 22:00 local time).
* **NFR-REL-001:** Booking transactions must strictly adhere to ACID properties to prevent data corruption or partial state writes.

### Scalability
* **NFR-SCL-001:** System shall support scaling up to 10,000 active students, 500 faculty members, and 50 departments without architectural refactoring.

### Usability & Accessibility
* **NFR-USA-001:** A student shall be able to complete an appointment request within **3 clicks** from the search landing page.
* **NFR-ACC-001:** UI layouts shall adhere to **WCAG 2.1 Level AA** standards (screen reader support, high contrast ratio, full keyboard navigation).

---

## 21. SECURITY & AUTHORIZATION REQUIREMENTS

* **SEC-001 (Password Security):** All user passwords must be hashed using `bcrypt` or `Argon2id` prior to storage. Plaintext passwords shall never be logged or stored.
* **SEC-002 (Session Integrity):** Authentication tokens (JWT / Session Cookies) must be signed, encrypted, transmitted over HTTPS, and configured with `HttpOnly` and `SameSite=Strict` flags.
* **SEC-003 (Access Control Enforcement):** Every API endpoint must validate the authenticated user's role and ownership rights (e.g., a student cannot view another student's private appointment notes or accept faculty requests).
* **SEC-004 (Input Sanitization):** All input fields (reasons, bios, agendas) must undergo strict server-side validation and HTML sanitization to prevent XSS and SQL Injection attacks.
* **SEC-005 (Rate Limiting):** API endpoints shall enforce rate limits (e.g., maximum 10 booking requests per minute per IP/User) to prevent automated denial-of-service or slot-scraping attacks.

---

## 22. EDGE CASES & SYSTEM BEHAVIOR

| Category | Edge Case Scenario | Expected System Behavior |
| :--- | :--- | :--- |
| **Availability** | Faculty has no regular or temporary availability defined. | Engine exposes zero bookable slots. Displays helper message: *"Faculty has not published availability."* |
| **Availability** | Temporary availability posted starting in the past. | Validation error: `INVALID_START_TIME`. Start time must be $\ge \text{current\_time} + \text{min\_notice}$. |
| **Availability** | Temporary availability expires while student is viewing profile. | Submitting request triggers `SLOT_EXPIRED` validation. UI prompts student to select an updated slot. |
| **Availability** | Faculty alters regular schedule after appointments exist. | Existing appointments remain untouched in database. New schedule rule applies only to unbooked intervals. |
| **Leave** | Faculty marks leave on a day with 5 accepted appointments. | All 5 appointments transition to `CANCELLED`. Students notified immediately with leave details. |
| **Leave** | Half-day morning leave (`08:00-13:00`) overlaps regular schedule (`09:00-12:00`). | Morning regular schedule is completely suppressed. Afternoon schedule (`14:00-17:00`) remains active. |
| **Booking** | Two students click "Request Slot" at identical millisecond. | Transaction lock grants slot to Student A. Student B receives `SLOT_TAKEN` error and refreshed UI. |
| **Booking** | Student attempts booking 15 minutes before slot start time. | Blocked by Min Advance Notice rule (2h requirement). Error: `INSUFFICIENT_LEAD_TIME`. |
| **Booking** | Appointment duration crosses midnight (`23:45 - 00:15`). | System rejects slots crossing midnight (`00:00:00` boundary). Slots must reside within a single calendar day. |
| **Rescheduling** | Proposed new slot is booked by another student before target student responds. | Proposal expires automatically. Original student is alerted that proposed slot is no longer available. |
| **Account** | Faculty account is deactivated by Admin while appointments exist. | All future pending/accepted appointments auto-cancel. Profile hidden from student search. |

---

## 23. MVP SCOPE (MoSCoW PRIORITIZATION)

### MUST HAVE (Core MVP Requirements)

* User Authentication & Role-Based Access Control (Student, Faculty, Admin).
* Faculty Profile Management & Public Search / Filtering.
* Regular Weekly Availability definition & storage.
* One-Time Temporary Availability publishing & auto-expiration.
* One-Time Temporary Unavailability (Blocking) & Leave declaration.
* Dynamic Slot Generation Engine implementing the 5-tier Precedence Model.
* Core Appointment Request Lifecycle (`REQUESTED`, `ACCEPTED`, `REJECTED`, `RESCHEDULE_PROPOSED`, `CANCELLED`, `COMPLETED`, `NO_SHOW`).
* Concurrency Protection against double-booking (`FR-CON-001`).
* In-App Real-Time Notifications feed.
* Basic Admin User & Department Management.

### SHOULD HAVE (Immediate Post-MVP / Phase 1.5)

* Email notifications via SMTP/SendGrid gateway.
* Export appointment to `.ics` / iCal file download.
* Advanced Admin analytics dashboard with visual charts.

### NICE TO HAVE (Future Scope)

* Automated 2-way Google Calendar / Outlook sync.
* Real-time WebSocket pushing for instant UI updates without polling.
* SMS / WhatsApp notification integration.

---

## 24. FUTURE SCOPE

The architecture created in subsequent phases shall be designed with clean interfaces to accommodate the following future extensions without breaking core models:

1. **Third-Party Calendar Integration:** Two-way sync with Google Calendar, Microsoft Outlook, and Apple iCal via OAuth2.
2. **Real-Time WebSockets:** Push slot updates and notification badges instantly without client polling.
3. **Group Consultations & Viva Scheduling:** Allow faculty to open slots for up to $N$ students simultaneously (e.g., group project reviews or viva panels).
4. **Waitlist & Queue Management:** Enable students to join a waiting list for popular faculty slots; auto-notify waitlisted students when a cancellation occurs.
5. **QR Code Check-in:** Allow students to scan a QR code outside a professor's office to mark physical arrival and transition appointment state to `COMPLETED`.

---

## 25. ACCEPTANCE CRITERIA

### AC-001 — Regular Availability Calculation
* **GIVEN** a faculty member has defined regular availability on Mondays from `09:00` to `12:00`,
* **WHEN** a student views the faculty's calendar for a future Monday (within 14 days and > 2h lead time),
* **THEN** the system displays 30-minute bookable slots (`09:00-09:30`, `09:30-10:00`, `10:00-10:30`, `10:30-11:00`, `11:00-11:30`, `11:30-12:00`).

### AC-002 — Temporary Availability Pop-Up
* **GIVEN** a faculty member publishes temporary availability for today from `11:15` to `11:45`,
* **WHEN** eligible students view the faculty profile,
* **THEN** the `11:15-11:45` slot becomes immediately visible and bookable, and automatically disappears when `current_time > 11:45`.

### AC-003 — Leave Suppression
* **GIVEN** a faculty member has marked Full-Day Leave for October 24th,
* **WHEN** any student attempts to view availability for October 24th,
* **THEN** zero bookable slots are exposed and an official leave indicator banner is displayed.

### AC-004 — Concurrency Protection
* **GIVEN** Student A and Student B simultaneously attempt to book the `10:00-10:30` slot for Professor X,
* **WHEN** both requests hit the system at the exact same time,
* **THEN** exactly one request transitions to `REQUESTED`, while the second request fails with HTTP 409 `SLOT_NO_LONGER_AVAILABLE`.

### AC-005 — Faculty Reschedule Proposal
* **GIVEN** an accepted appointment exists for Tuesday at `14:00`,
* **WHEN** the faculty proposes rescheduling to Wednesday at `10:00`,
* **THEN** the status transitions to `RESCHEDULE_PROPOSED`, Wednesday `10:00` is soft-locked for the student, and Tuesday `14:00` is released to the open pool.

---

## 26. AMBIGUOUS DECISIONS & ARCHITECTURAL RATIONALES

To ensure zero ambiguity during architecture and database design, key business rules were systematically analyzed and resolved as documented below:

### Decision 1: Should Faculty Leave require prior Admin Approval?
* **Options Considered:**
  * *Option A:* Leave requires mandatory Admin approval before taking effect on schedules.
  * *Option B:* Faculty self-declares leave; it takes immediate effect on schedules with Admin notification.
* **Recommended Choice:** **Option B (Self-Declaration).**
* **Rationale:** Academic appointments are time-sensitive. Requiring admin approval creates operational bottlenecks where students might continue booking slots during a professor's sudden illness or urgent conference travel. Self-declaration ensures student calendars are protected instantly.

### Decision 2: Can Temporary Availability override an approved Leave entry?
* **Options Considered:**
  * *Option A:* Yes, temporary availability acts as absolute top-priority override.
  * *Option B:* No, Leave strictly blocks all availability. Faculty must explicitly cancel/modify leave first.
* **Recommended Choice:** **Option B (Leave is Strict).**
* **Rationale:** Allowing temporary availability to silently punch holes through official Leave records creates contradictory institutional audit data (showing a user simultaneously "on official leave" and "conducting meetings"). Enforcing leave cancellation maintains data integrity.

### Decision 3: Does a `REQUESTED` (Pending) appointment block the slot for other students?
* **Options Considered:**
  * *Option A:* Yes, pending request soft-locks the slot immediately.
  * *Option B:* No, slot remains open until faculty explicitly accepts one request; remaining requests are rejected.
* **Recommended Choice:** **Option A (Pending Holds Slot).**
* **Rationale:** Option B encourages race conditions and student frustration where multiple students believe they have requested an open slot, only for all but one to be rejected. Soft-locking ensures fair FIFO processing.

### Decision 4: Can Students book faculty outside their own department?
* **Options Considered:**
  * *Option A:* No, restricted strictly to cross-referenced student-faculty department IDs.
  * *Option B:* Yes, cross-departmental booking is permitted system-wide.
* **Recommended Choice:** **Option B (System-wide Cross-Department Booking).**
* **Rationale:** In modern universities, students frequently consult interdisciplinary advisors, minor subject professors, or research supervisors outside their home department.

---

## 27. FINAL REQUIREMENTS SUMMARY

### Product Vision
The **Faculty Availability & Appointment Scheduler** is a specialized, dynamic scheduling platform for higher education that calculates true real-time faculty availability by combining regular schedules, temporary pop-up hours, blocked periods, leave declarations, and existing appointments under strict mathematical precedence rules.

### User Roles
* **Student:** Search faculty, view dynamic slots, request/cancel appointments, respond to reschedule proposals.
* **Faculty:** Manage regular hours, publish temporary availability, post blocks, mark leave, accept/reject/reschedule requests.
* **Admin:** System governance, user lifecycle management, department setup, global policy configuration, audit inspection.

### Core Scheduling Logic
$$\text{Available Slots} = \Big( \big( \text{Regular} \setminus \text{Temp Blocks} \big) \cup \text{Temp Availability} \Big) \setminus \Big( \text{Leave} \cup \text{Appointments} \Big)$$

### Core MVP Deliverables
1. RBAC Authentication & Profile Management.
2. 5-Tier Precedence Dynamic Availability Engine.
3. Temporary Availability & Blocking Workflows.
4. Deterministic Appointment Lifecycle State Machine.
5. Atomic Concurrency Lock (`FR-CON-001`).
6. Real-time In-App Notification Feed.
7. Governance Admin Dashboard.

### Top 5 Technical Challenges & Mitigation Strategies
1. **Sub-second Dynamic Availability Calculation:** Mitigated by interval set algebra executed efficiently in backend service memory or optimized database SQL windowing.
2. **Zero Double-Booking under Concurrent Race Conditions:** Mitigated by database transaction isolation (`SERIALIZABLE` / pessimistic row locks) on slot reservation.
3. **Complex Schedule Overlap Edge Cases:** Mitigated by strict mathematical precedence hierarchy (Tiers 1 to 5).
4. **State Machine Consistency Across Role Actions:** Mitigated by explicit transition validation matrices prohibiting illegal state jumps.
5. **Timezone & Date Boundary Formatting:** Mitigated by storing all timestamps in standard UTC ISO 8601 strings and rendering in local institutional time.
