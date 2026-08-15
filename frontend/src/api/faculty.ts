import { apiClient } from './client';
import { FacultyPublicProfile } from '../types';

export const facultyApi = {
  listPublicFaculty: async (departmentId?: string): Promise<FacultyPublicProfile[]> => {
    const params = departmentId ? { department_id: departmentId } : {};
    const res = await apiClient.get<FacultyPublicProfile[]>('/api/v1/users/faculty', { params });
    return res.data;
  },

  getFacultyPublicProfile: async (facultyId: string): Promise<FacultyPublicProfile> => {
    const res = await apiClient.get<FacultyPublicProfile>(`/api/v1/users/faculty/${facultyId}`);
    return res.data;
  },
};
