export type UserRole = 'ADMIN' | 'FACULTY' | 'STUDENT';
export type UserStatus = 'ACTIVE' | 'SUSPENDED' | 'DEACTIVATED';
export type MeetingMode = 'IN_PERSON' | 'VIRTUAL' | 'HYBRID';

export type AppointmentStatus =
  | 'REQUESTED'
  | 'ACCEPTED'
  | 'REJECTED'
  | 'CANCELLED'
  | 'COMPLETED'
  | 'RESCHEDULE_PROPOSED';

export type LeaveType =
  | 'FULL_DAY'
  | 'HALF_DAY_MORNING'
  | 'HALF_DAY_AFTERNOON'
  | 'MULTI_DAY';

export type LeaveStatus = 'APPROVED' | 'PENDING' | 'CANCELLED';

export interface Department {
  id: string;
  code: string;
  name: string;
  building?: string | null;
  created_at: string;
}

export interface StudentProfile {
  id: string;
  user_id: string;
  student_id_number: string;
  major: string;
  created_at: string;
}

export interface FacultyProfile {
  id: string;
  user_id: string;
  department_id: string;
  department?: Department | null;
  employee_id_number: string;
  title: string;
  office_location: string;
  bio?: string | null;
  meeting_mode: MeetingMode;
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  status: UserStatus;
  created_at: string;
  updated_at: string;
  student_profile?: StudentProfile | null;
  faculty_profile?: FacultyProfile | null;
}

export interface FacultyPublicProfile {
  id: string;
  user_id: string;
  full_name: string;
  email: string;
  title: string;
  office_location: string;
  bio?: string | null;
  meeting_mode: MeetingMode;
  department_id: string;
  department_name: string;
  department_code: string;
}

export interface RegularAvailability {
  id: string;
  faculty_id: string;
  day_of_week: number; // 0=Mon, 6=Sun
  start_time: string; // "09:00:00"
  end_time: string;   // "12:00:00"
  slot_duration_minutes: number;
  is_active: boolean;
  created_at: string;
}

export interface TemporaryAvailability {
  id: string;
  faculty_id: string;
  date: string; // "2026-08-24"
  start_time: string;
  end_time: string;
  reason?: string | null;
  created_at: string;
}

export interface BlockedSlot {
  id: string;
  faculty_id: string;
  start_datetime: string;
  end_datetime: string;
  reason: string;
  created_at: string;
}

export interface LeaveRecord {
  id: string;
  faculty_id: string;
  start_date: string;
  end_date: string;
  leave_type: LeaveType;
  status: LeaveStatus;
  reason: string;
  created_at: string;
}

export interface TimeInterval {
  start_time: string; // "09:00"
  end_time: string;   // "12:00"
}

export interface BookableSlot {
  start_datetime: string;
  end_datetime: string;
  start_time: string; // "09:00"
  end_time: string;   // "09:30"
  duration_minutes: number;
  status: string; // "AVAILABLE"
}

export interface FacultyAvailabilityResponse {
  faculty_id: string;
  date: string;
  timezone: string;
  day_of_week: number;
  is_on_leave: boolean;
  available_windows: TimeInterval[];
  slots: BookableSlot[];
  total_slots: number;
  leave_reason?: string | null;
}

export interface StudentSummary {
  id: string;
  user_id: string;
  full_name: string;
  email: string;
  student_id_number: string;
  major: string;
}

export interface FacultySummary {
  id: string;
  user_id: string;
  full_name: string;
  email: string;
  employee_id_number: string;
  title: string;
  office_location: string;
  department_name?: string | null;
}

export interface Appointment {
  id: string;
  student_id: string;
  faculty_id: string;
  student?: StudentSummary | null;
  faculty?: FacultySummary | null;
  date: string;
  start_time: string; // "09:00:00"
  end_time: string;   // "09:30:00"
  duration_minutes: number;
  status: AppointmentStatus;
  reason: string;
  faculty_notes?: string | null;
  cancellation_reason?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApiErrorDetail {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  timestamp?: string;
}

export interface ApiErrorResponse {
  error: ApiErrorDetail;
}
