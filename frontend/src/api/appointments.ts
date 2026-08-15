import { apiClient } from './client';
import { Appointment, AppointmentStatus } from '../types';

export interface AppointmentCreatePayload {
  faculty_id: string;
  date: string;
  start_time: string;
  end_time: string;
  reason: string;
}

export interface AppointmentFilterParams {
  status?: AppointmentStatus;
  date?: string;
  from_date?: string;
  to_date?: string;
}

export interface AppointmentActionPayload {
  reason?: string;
  faculty_notes?: string;
}

export const appointmentsApi = {
  bookAppointment: async (payload: AppointmentCreatePayload): Promise<Appointment> => {
    const res = await apiClient.post<Appointment>('/api/v1/appointments', payload);
    return res.data;
  },

  listMyAppointments: async (filters?: AppointmentFilterParams): Promise<Appointment[]> => {
    const res = await apiClient.get<Appointment[]>('/api/v1/appointments/me', { params: filters });
    return res.data;
  },

  getAppointmentDetails: async (id: string): Promise<Appointment> => {
    const res = await apiClient.get<Appointment>(`/api/v1/appointments/${id}`);
    return res.data;
  },

  acceptAppointment: async (id: string, notes?: string): Promise<Appointment> => {
    const payload = notes ? { faculty_notes: notes } : {};
    const res = await apiClient.put<Appointment>(`/api/v1/appointments/${id}/accept`, payload);
    return res.data;
  },

  rejectAppointment: async (id: string, reason?: string): Promise<Appointment> => {
    const payload = reason ? { reason } : {};
    const res = await apiClient.put<Appointment>(`/api/v1/appointments/${id}/reject`, payload);
    return res.data;
  },

  cancelAppointment: async (id: string, reason?: string): Promise<Appointment> => {
    const payload = reason ? { reason } : {};
    const res = await apiClient.put<Appointment>(`/api/v1/appointments/${id}/cancel`, payload);
    return res.data;
  },

  completeAppointment: async (id: string): Promise<Appointment> => {
    const res = await apiClient.put<Appointment>(`/api/v1/appointments/${id}/complete`);
    return res.data;
  },
};
