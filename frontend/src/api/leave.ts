import { apiClient } from './client';
import { LeaveRecord, LeaveType } from '../types';

export interface LeaveCreatePayload {
  start_date: string;
  end_date: string;
  leave_type: LeaveType;
  reason: string;
}

export interface LeaveUpdatePayload {
  reason?: string;
}

export const leaveApi = {
  listLeaves: async (facultyId?: string): Promise<LeaveRecord[]> => {
    const params = facultyId ? { faculty_id: facultyId } : {};
    const res = await apiClient.get<LeaveRecord[]>('/api/v1/leave', { params });
    return res.data;
  },

  createLeave: async (payload: LeaveCreatePayload): Promise<LeaveRecord> => {
    const res = await apiClient.post<LeaveRecord>('/api/v1/leave', payload);
    return res.data;
  },

  updateLeave: async (id: string, payload: LeaveUpdatePayload): Promise<LeaveRecord> => {
    const res = await apiClient.put<LeaveRecord>(`/api/v1/leave/${id}`, payload);
    return res.data;
  },

  deleteLeave: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/leave/${id}`);
  },
};
