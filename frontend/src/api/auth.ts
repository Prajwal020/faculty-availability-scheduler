import { apiClient } from './client';
import { User, MeetingMode } from '../types';

export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterStudentPayload {
  email: string;
  password: string;
  full_name: string;
  student_id_number: string;
  major: string;
}

export interface RegisterFacultyPayload {
  email: string;
  password: string;
  full_name: string;
  employee_id_number: string;
  department_id: string;
  title: string;
  office_location: string;
  bio?: string;
  meeting_mode?: MeetingMode;
}

export const authApi = {
  login: async (payload: LoginPayload): Promise<AuthResponse> => {
    const res = await apiClient.post<AuthResponse>('/api/v1/auth/login', payload);
    return res.data;
  },

  getMe: async (): Promise<User> => {
    const res = await apiClient.get<User>('/api/v1/auth/me');
    return res.data;
  },

  registerStudent: async (payload: RegisterStudentPayload): Promise<AuthResponse> => {
    const res = await apiClient.post<AuthResponse>('/api/v1/auth/register/student', payload);
    return res.data;
  },

  registerFaculty: async (payload: RegisterFacultyPayload): Promise<AuthResponse> => {
    const res = await apiClient.post<AuthResponse>('/api/v1/auth/register/faculty', payload);
    return res.data;
  },
};
