import { apiClient } from './client';
import { Department } from '../types';

export interface DepartmentCreatePayload {
  code: string;
  name: string;
  building?: string;
}

export interface DepartmentUpdatePayload {
  code?: string;
  name?: string;
  building?: string;
}

export const departmentsApi = {
  listDepartments: async (): Promise<Department[]> => {
    const res = await apiClient.get<Department[]>('/api/v1/departments');
    return res.data;
  },

  getDepartment: async (id: string): Promise<Department> => {
    const res = await apiClient.get<Department>(`/api/v1/departments/${id}`);
    return res.data;
  },

  createDepartment: async (payload: DepartmentCreatePayload): Promise<Department> => {
    const res = await apiClient.post<Department>('/api/v1/departments', payload);
    return res.data;
  },

  updateDepartment: async (id: string, payload: DepartmentUpdatePayload): Promise<Department> => {
    const res = await apiClient.put<Department>(`/api/v1/departments/${id}`, payload);
    return res.data;
  },
};
