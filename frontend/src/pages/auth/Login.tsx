import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { GraduationCap, AlertCircle, ArrowRight, Shield, User, School } from 'lucide-react';

export const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please provide both email and password.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const user = await login(email, password);
      const from = (location.state as any)?.from?.pathname;

      if (from) {
        navigate(from, { replace: true });
      } else if (user.role === 'STUDENT') {
        navigate('/student/dashboard', { replace: true });
      } else if (user.role === 'FACULTY') {
        navigate('/faculty/dashboard', { replace: true });
      } else if (user.role === 'ADMIN') {
        navigate('/admin/dashboard', { replace: true });
      } else {
        navigate('/', { replace: true });
      }
    } catch (err: any) {
      setError(err.message || 'Invalid email or password. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickLogin = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError(null);
  };

  return (
    <div className="min-h-screen flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8 bg-slate-900 selection:bg-brand-500 selection:text-white">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-brand-600 text-white shadow-lg mb-4">
          <GraduationCap className="w-8 h-8" />
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white font-sans">
          Academic Scheduler
        </h1>
        <p className="mt-2 text-xs sm:text-sm text-slate-400">
          Faculty Availability & Real-Time Appointment Booking
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-xl rounded-2xl sm:px-10 border border-slate-200">
          {error && (
            <div className="mb-5 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2.5">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Institutional Email"
              type="email"
              placeholder="name@institution.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
            />

            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <Button type="submit" className="w-full mt-2" isLoading={isLoading} rightIcon={<ArrowRight className="w-4 h-4" />}>
              Sign In
            </Button>
          </form>

          {/* Quick Demo Seed Credentials */}
          <div className="mt-6 pt-6 border-t border-slate-100">
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-500 text-center mb-3">
              One-Click Demo Accounts
            </p>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleQuickLogin('student.alex@institution.edu', 'StudentPassword123!')}
                className="p-2.5 rounded-lg border border-slate-200 hover:border-brand-500 hover:bg-brand-50/40 text-center transition flex flex-col items-center gap-1 group"
              >
                <School className="w-4 h-4 text-slate-500 group-hover:text-brand-600" />
                <span className="text-[11px] font-semibold text-slate-800">Student</span>
                <span className="text-[9px] text-slate-600">Alex R.</span>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin('prof.sharma@institution.edu', 'FacultyPassword123!')}
                className="p-2.5 rounded-lg border border-slate-200 hover:border-brand-500 hover:bg-brand-50/40 text-center transition flex flex-col items-center gap-1 group"
              >
                <User className="w-4 h-4 text-slate-500 group-hover:text-brand-600" />
                <span className="text-[11px] font-semibold text-slate-800">Faculty</span>
                <span className="text-[9px] text-slate-600">Dr. Sharma</span>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin('admin@institution.edu', 'AdminPassword123!')}
                className="p-2.5 rounded-lg border border-slate-200 hover:border-brand-500 hover:bg-brand-50/40 text-center transition flex flex-col items-center gap-1 group"
              >
                <Shield className="w-4 h-4 text-slate-500 group-hover:text-brand-600" />
                <span className="text-[11px] font-semibold text-slate-800">Admin</span>
                <span className="text-[9px] text-slate-600">System</span>
              </button>
            </div>
          </div>
        </div>

        <p className="text-center text-xs text-slate-400 mt-6">
          Asia/Kolkata Institutional Timezone Standard · All rights reserved
        </p>
      </div>
    </div>
  );
};
