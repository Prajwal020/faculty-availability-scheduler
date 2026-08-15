import React from 'react';
import { Navigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { UserRole } from '../../types';
import { ShieldAlert, ArrowLeft, Loader2 } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const { user, isLoading, isAuthenticated } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50">
        <Loader2 className="w-10 h-10 text-brand-600 animate-spin mb-4" />
        <p className="text-slate-600 text-sm font-medium">Authenticating session...</p>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (user.status !== 'ACTIVE') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-slate-50 text-center">
        <div className="w-16 h-16 bg-red-100 text-red-600 rounded-full flex items-center justify-center mb-4">
          <ShieldAlert className="w-8 h-8" />
        </div>
        <h1 className="text-2xl font-bold text-slate-900 mb-2">Account Inactive</h1>
        <p className="text-slate-600 max-w-md mb-6">
          Your account status is currently <strong>{user.status}</strong>. Please contact your institution administrator.
        </p>
        <Link
          to="/login"
          className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition"
        >
          <ArrowLeft className="w-4 h-4" /> Return to Login
        </Link>
      </div>
    );
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    const dashboardPath =
      user.role === 'STUDENT'
        ? '/student/dashboard'
        : user.role === 'FACULTY'
        ? '/faculty/dashboard'
        : '/admin/dashboard';

    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-slate-50 text-center">
        <div className="w-16 h-16 bg-amber-100 text-amber-600 rounded-full flex items-center justify-center mb-4">
          <ShieldAlert className="w-8 h-8" />
        </div>
        <h1 className="text-2xl font-bold text-slate-900 mb-2">403 — Access Denied</h1>
        <p className="text-slate-600 max-w-md mb-6">
          You do not have permission to access this area. Your current role is <strong>{user.role}</strong>.
        </p>
        <Link
          to={dashboardPath}
          className="inline-flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition"
        >
          <ArrowLeft className="w-4 h-4" /> Go to Your Dashboard
        </Link>
      </div>
    );
  }

  return <>{children}</>;
};
