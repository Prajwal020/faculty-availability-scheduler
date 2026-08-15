import { apiClient } from './client';
import {
  FacultyAvailabilityResponse,
  RegularAvailability,
  TemporaryAvailability,
  BlockedSlot,
} from '../types';

export interface RegularAvailabilityCreatePayload {
  day_of_week: number;
  start_time: string;
  end_time: string;
  slot_duration_minutes?: number;
  is_active?: boolean;
}

export interface RegularAvailabilityUpdatePayload {
  start_time?: string;
  end_time?: string;
  slot_duration_minutes?: number;
  is_active?: boolean;
}

export interface TemporaryAvailabilityCreatePayload {
  date: string;
  start_time: string;
  end_time: string;
  reason?: string;
}

export interface BlockedSlotCreatePayload {
  start_datetime: string;
  end_datetime: string;
  reason: string;
}

export const availabilityApi = {
  getFacultyAvailability: async (
    facultyId: string,
    date: string,
    durationMinutes: number = 30
  ): Promise<FacultyAvailabilityResponse> => {
    const res = await apiClient.get<FacultyAvailabilityResponse>(
      `/api/v1/availability/${facultyId}`,
      {
        params: {
          date,
          duration: durationMinutes,
        },
      }
    );
    return res.data;
  },

  // Regular Availability
  listRegular: async (facultyId?: string): Promise<RegularAvailability[]> => {
    const params = facultyId ? { faculty_id: facultyId } : {};
    const res = await apiClient.get<RegularAvailability[]>('/api/v1/availability/regular', { params });
    return res.data;
  },

  createRegular: async (payload: RegularAvailabilityCreatePayload): Promise<RegularAvailability> => {
    const res = await apiClient.post<RegularAvailability>('/api/v1/availability/regular', payload);
    return res.data;
  },

  updateRegular: async (id: string, payload: RegularAvailabilityUpdatePayload): Promise<RegularAvailability> => {
    const res = await apiClient.put<RegularAvailability>(`/api/v1/availability/regular/${id}`, payload);
    return res.data;
  },

  deleteRegular: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/availability/regular/${id}`);
  },

  // Temporary Availability
  listTemporary: async (facultyId?: string): Promise<TemporaryAvailability[]> => {
    const params = facultyId ? { faculty_id: facultyId } : {};
    const res = await apiClient.get<TemporaryAvailability[]>('/api/v1/availability/temporary', { params });
    return res.data;
  },

  createTemporary: async (payload: TemporaryAvailabilityCreatePayload): Promise<TemporaryAvailability> => {
    const res = await apiClient.post<TemporaryAvailability>('/api/v1/availability/temporary', payload);
    return res.data;
  },

  deleteTemporary: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/availability/temporary/${id}`);
  },

  // Blocked Slots
  listBlocked: async (facultyId?: string): Promise<BlockedSlot[]> => {
    const params = facultyId ? { faculty_id: facultyId } : {};
    const res = await apiClient.get<BlockedSlot[]>('/api/v1/availability/blocked', { params });
    return res.data;
  },

  createBlocked: async (payload: BlockedSlotCreatePayload): Promise<BlockedSlot> => {
    const res = await apiClient.post<BlockedSlot>('/api/v1/availability/blocked', payload);
    return res.data;
  },

  deleteBlocked: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/availability/blocked/${id}`);
  },
};
