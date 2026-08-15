import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AdminFacultyManagement } from '../pages/admin/FacultyManagement';
import { facultyApi } from '../api/faculty';
import { departmentsApi } from '../api/departments';
import { FacultyPublicProfile, Department } from '../types';

vi.mock('../api/faculty', () => ({
  facultyApi: {
    listPublicFaculty: vi.fn(),
  },
}));

vi.mock('../api/departments', () => ({
  departmentsApi: {
    listDepartments: vi.fn(),
  },
}));

const mockFacultyList: FacultyPublicProfile[] = [
  {
    id: 'fac-1',
    user_id: 'user-1',
    full_name: 'Dr. Rajesh Sharma',
    email: 'prof.sharma@institution.edu',
    title: 'Professor & HOD',
    office_location: 'Turing Hall, Room 301',
    bio: 'Distributed Systems',
    meeting_mode: 'HYBRID',
    department_id: 'dept-1',
    department_name: 'Computer Science & Engineering',
    department_code: 'CS',
  },
  {
    id: 'fac-2',
    user_id: 'user-2',
    full_name: 'Dr. Ananya Menon',
    email: 'prof.menon@institution.edu',
    title: 'Associate Professor',
    office_location: 'Euler Block, Room 204',
    bio: 'Applied Statistics',
    meeting_mode: 'IN_PERSON',
    department_id: 'dept-2',
    department_name: 'Mathematics & Data Science',
    department_code: 'MATH',
  },
];

const mockDepartments: Department[] = [
  { id: 'dept-1', code: 'CS', name: 'Computer Science & Engineering', building: 'Turing Hall', created_at: '2026-08-15' },
  { id: 'dept-2', code: 'MATH', name: 'Mathematics & Data Science', building: 'Euler Block', created_at: '2026-08-15' },
];

const renderWithQueryClient = (ui: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
};

describe('AdminFacultyManagement Component', () => {
  it('fetches and renders all faculty profiles correctly', async () => {
    vi.mocked(facultyApi.listPublicFaculty).mockResolvedValue(mockFacultyList);
    vi.mocked(departmentsApi.listDepartments).mockResolvedValue(mockDepartments);

    renderWithQueryClient(<AdminFacultyManagement />);

    expect(await screen.findByText('Dr. Rajesh Sharma')).toBeInTheDocument();
    expect(screen.getByText('Dr. Ananya Menon')).toBeInTheDocument();
    expect(screen.getByText('Computer Science & Engineering')).toBeInTheDocument();
    expect(screen.getByText('Mathematics & Data Science')).toBeInTheDocument();
    expect(screen.getByText('Turing Hall, Room 301')).toBeInTheDocument();
    expect(screen.getByText('Euler Block, Room 204')).toBeInTheDocument();
  });

  it('filters faculty by search query', async () => {
    vi.mocked(facultyApi.listPublicFaculty).mockResolvedValue(mockFacultyList);
    vi.mocked(departmentsApi.listDepartments).mockResolvedValue(mockDepartments);

    renderWithQueryClient(<AdminFacultyManagement />);

    expect(await screen.findByText('Dr. Rajesh Sharma')).toBeInTheDocument();
    expect(screen.getByText('Dr. Ananya Menon')).toBeInTheDocument();

    const searchInput = screen.getByPlaceholderText(/Search by faculty name/);
    fireEvent.change(searchInput, { target: { value: 'Rajesh' } });

    expect(screen.getByText('Dr. Rajesh Sharma')).toBeInTheDocument();
    expect(screen.queryByText('Dr. Ananya Menon')).not.toBeInTheDocument();
  });
});
