import { apiClient } from './client';
import { User, UserRole, UserStatus, MeetingMode } from '../types';

export interface StudentProfileUpdatePayload {
  student_id_number?: string;
  major?: string;
  full_name?: string;
}

export interface FacultyProfileUpdatePayload {
  title?: string;
  office_location?: string;
  bio?: string;
  meeting_mode?: MeetingMode;
  department_id?: string;
  full_name?: string;
}

export interface AdminUserCreatePayload {
  email: string;
  password: string;
  full_name: string;
  role: UserRole;
}

export const usersApi = {
  getMe: async (): Promise<User> => {
    const res = await apiClient.get<User>('/api/v1/auth/me');
    return res.data;
  },

  updateStudentProfile: async (payload: StudentProfileUpdatePayload): Promise<User> => {
    const res = await apiClient.put<User>('/api/v1/users/students/me', payload);
    return res.data;
  },

  updateFacultyProfile: async (payload: FacultyProfileUpdatePayload): Promise<User> => {
    const res = await apiClient.put<User>('/api/v1/users/faculty/me', payload);
    return res.data;
  },

  // Admin User APIs
  listUsersAdmin: async (skip: number = 0, limit: number = 50): Promise<User[]> => {
    const res = await apiClient.get<User[]>('/api/v1/admin/users', { params: { skip, limit } });
    return res.data;
  },

  createUserAdmin: async (payload: AdminUserCreatePayload): Promise<User> => {
    const res = await apiClient.post<User>('/api/v1/admin/users/create', payload);
    return res.data;
  },

  updateUserStatusAdmin: async (userId: string, status: UserStatus): Promise<User> => {
    const res = await apiClient.patch<User>(`/api/v1/admin/users/${userId}/status`, { status });
    return res.data;
  },
};
