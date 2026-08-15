import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from '../components/layout/ProtectedRoute';
import * as AuthContextModule from '../context/AuthContext';
import { User } from '../types';

const mockStudentUser: User = {
  id: 'user-1',
  email: 'student@institution.edu',
  full_name: 'Student User',
  role: 'STUDENT',
  status: 'ACTIVE',
  created_at: '2026-08-15',
  updated_at: '2026-08-15',
};

const mockSuspendedUser: User = {
  ...mockStudentUser,
  status: 'SUSPENDED',
};

describe('ProtectedRoute Component', () => {
  it('renders children when user role matches allowedRoles', () => {
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
      user: mockStudentUser,
      token: 'valid-token',
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      refreshUser: vi.fn(),
      isAuthenticated: true,
      isStudent: true,
      isFaculty: false,
      isAdmin: false,
    });

    render(
      <MemoryRouter initialEntries={['/student/dashboard']}>
        <Routes>
          <Route
            path="/student/dashboard"
            element={
              <ProtectedRoute allowedRoles={['STUDENT']}>
                <div>Student Secret Dashboard</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Student Secret Dashboard')).toBeInTheDocument();
  });

  it('renders 403 — Access Denied when user role is not in allowedRoles', () => {
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
      user: mockStudentUser,
      token: 'valid-token',
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      refreshUser: vi.fn(),
      isAuthenticated: true,
      isStudent: true,
      isFaculty: false,
      isAdmin: false,
    });

    render(
      <MemoryRouter initialEntries={['/admin/dashboard']}>
        <Routes>
          <Route
            path="/admin/dashboard"
            element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <div>Admin Secret Dashboard</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('403 — Access Denied')).toBeInTheDocument();
    expect(screen.queryByText('Admin Secret Dashboard')).not.toBeInTheDocument();
  });

  it('renders Account Inactive when user status is SUSPENDED', () => {
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
      user: mockSuspendedUser,
      token: 'valid-token',
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      refreshUser: vi.fn(),
      isAuthenticated: true,
      isStudent: true,
      isFaculty: false,
      isAdmin: false,
    });

    render(
      <MemoryRouter initialEntries={['/student/dashboard']}>
        <Routes>
          <Route
            path="/student/dashboard"
            element={
              <ProtectedRoute allowedRoles={['STUDENT']}>
                <div>Student Secret Dashboard</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Account Inactive')).toBeInTheDocument();
    expect(screen.queryByText('Student Secret Dashboard')).not.toBeInTheDocument();
  });
});
