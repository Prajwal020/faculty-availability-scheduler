import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';

// Auth Pages
import { Login } from './pages/auth/Login';

// Student Pages
import { StudentDashboard } from './pages/student/Dashboard';
import { FacultyDirectory } from './pages/student/FacultyDirectory';
import { FacultyProfile } from './pages/student/FacultyProfile';
import { StudentAppointmentsList } from './pages/student/AppointmentsList';
import { StudentAppointmentDetails } from './pages/student/AppointmentDetails';

// Faculty Pages
import { FacultyDashboard } from './pages/faculty/Dashboard';
import { FacultyAppointmentRequests } from './pages/faculty/AppointmentRequests';
import { FacultySchedule } from './pages/faculty/Schedule';
import { FacultyAvailabilityManager } from './pages/faculty/AvailabilityManager';
import { FacultyTemporaryAvailability } from './pages/faculty/TemporaryAvailability';
import { FacultyBlockedSlots } from './pages/faculty/BlockedSlots';
import { FacultyLeaveManager } from './pages/faculty/LeaveManager';

// Admin Pages
import { AdminDashboard } from './pages/admin/Dashboard';
import { AdminFacultyManagement } from './pages/admin/FacultyManagement';
import { AdminUserManagement } from './pages/admin/UserManagement';
import { AdminDepartmentManagement } from './pages/admin/DepartmentManagement';

// Shared Pages
import { Profile } from './pages/Profile';
import { NotFound } from './pages/NotFound';

const RootRedirect: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return null;
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  switch (user.role) {
    case 'STUDENT':
      return <Navigate to="/student/dashboard" replace />;
    case 'FACULTY':
      return <Navigate to="/faculty/dashboard" replace />;
    case 'ADMIN':
      return <Navigate to="/admin/dashboard" replace />;
    default:
      return <Navigate to="/login" replace />;
  }
};

export const App: React.FC = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<Login />} />

      {/* Root redirect based on role */}
      <Route path="/" element={<RootRedirect />} />

      {/* Protected App Shell */}
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        {/* Student Portal */}
        <Route
          path="/student/dashboard"
          element={
            <ProtectedRoute allowedRoles={['STUDENT']}>
              <StudentDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/faculty"
          element={
            <ProtectedRoute allowedRoles={['STUDENT']}>
              <FacultyDirectory />
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/faculty/:facultyId"
          element={
            <ProtectedRoute allowedRoles={['STUDENT']}>
              <FacultyProfile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/appointments"
          element={
            <ProtectedRoute allowedRoles={['STUDENT']}>
              <StudentAppointmentsList />
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/appointments/:id"
          element={
            <ProtectedRoute allowedRoles={['STUDENT']}>
              <StudentAppointmentDetails />
            </ProtectedRoute>
          }
        />

        {/* Faculty Portal */}
        <Route
          path="/faculty/dashboard"
          element={
            <ProtectedRoute allowedRoles={['FACULTY']}>
              <FacultyDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/faculty/requests"
          element={
            <ProtectedRoute allowedRoles={['FACULTY']}>
              <FacultyAppointmentRequests />
            </ProtectedRoute>
          }
        />
        <Route
          path="/faculty/schedule"
          element={
            <ProtectedRoute allowedRoles={['FACULTY']}>
              <FacultySchedule />
            </ProtectedRoute>
          }
        />
        <Route
          path="/faculty/availability"
          element={
            <ProtectedRoute allowedRoles={['FACULTY']}>
              <FacultyAvailabilityManager />
            </ProtectedRoute>
          }
        />
        <Route
          path="/faculty/temporary"
          element={
            <ProtectedRoute allowedRoles={['FACULTY']}>
              <FacultyTemporaryAvailability />
            </ProtectedRoute>
          }
        />
        <Route
          path="/faculty/blocks"
          element={
            <ProtectedRoute allowedRoles={['FACULTY']}>
              <FacultyBlockedSlots />
            </ProtectedRoute>
          }
        />
        <Route
          path="/faculty/leave"
          element={
            <ProtectedRoute allowedRoles={['FACULTY']}>
              <FacultyLeaveManager />
            </ProtectedRoute>
          }
        />

        {/* Admin Portal */}
        <Route
          path="/admin/dashboard"
          element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/faculty"
          element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <AdminFacultyManagement />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/users"
          element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <AdminUserManagement />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/departments"
          element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <AdminDepartmentManagement />
            </ProtectedRoute>
          }
        />

        {/* Shared User Profile */}
        <Route path="/profile" element={<Profile />} />
      </Route>

      {/* 404 Catch All */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};
