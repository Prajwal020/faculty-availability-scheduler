import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { cn } from '../../utils/cn';
import {
  LayoutDashboard,
  Users,
  Calendar,
  Clock,
  Ban,
  CalendarOff,
  UserCheck,
  Building2,
  CalendarRange,
  GraduationCap,
  Sparkles,
} from 'lucide-react';

interface SidebarProps {
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onCloseMobile }) => {
  const { user, isStudent, isFaculty, isAdmin } = useAuth();

  const studentLinks = [
    { to: '/student/dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
    { to: '/student/faculty', label: 'Find Faculty', icon: <Users className="w-4 h-4" /> },
    { to: '/student/appointments', label: 'My Appointments', icon: <CalendarRange className="w-4 h-4" /> },
  ];

  const facultyLinks = [
    { to: '/faculty/dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
    { to: '/faculty/requests', label: 'Appointment Requests', icon: <UserCheck className="w-4 h-4" /> },
    { to: '/faculty/schedule', label: 'My Schedule', icon: <Calendar className="w-4 h-4" /> },
    { to: '/faculty/availability', label: 'Weekly Hours', icon: <Clock className="w-4 h-4" /> },
    { to: '/faculty/temporary', label: 'Pop-up Hours', icon: <Sparkles className="w-4 h-4" /> },
    { to: '/faculty/blocks', label: 'Blocked Periods', icon: <Ban className="w-4 h-4" /> },
    { to: '/faculty/leave', label: 'Leave Declarations', icon: <CalendarOff className="w-4 h-4" /> },
  ];

  const adminLinks = [
    { to: '/admin/dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
    { to: '/admin/faculty', label: 'Faculty Directory', icon: <GraduationCap className="w-4 h-4" /> },
    { to: '/admin/users', label: 'User Management', icon: <Users className="w-4 h-4" /> },
    { to: '/admin/departments', label: 'Departments', icon: <Building2 className="w-4 h-4" /> },
  ];

  const links = isStudent ? studentLinks : isFaculty ? facultyLinks : isAdmin ? adminLinks : [];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col h-full border-r border-slate-800">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-brand-600 flex items-center justify-center text-white font-bold text-lg shadow-sm">
          <GraduationCap className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-sm font-bold text-white tracking-tight leading-tight">
            Academic Scheduler
          </h2>
          <p className="text-[11px] text-slate-400 font-medium">Faculty Availability</p>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
          {user?.role} Portal
        </div>
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            onClick={onCloseMobile}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition-all select-none',
                isActive
                  ? 'bg-brand-600 text-white shadow-xs font-bold'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              )
            }
          >
            <span className="shrink-0">{link.icon}</span>
            <span>{link.label}</span>
          </NavLink>
        ))}
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800 text-[11px] text-slate-400 space-y-1 bg-slate-950/40">
        <div className="flex items-center justify-between text-slate-300">
          <span>Timezone</span>
          <span className="font-semibold text-brand-400">IST (UTC+05:30)</span>
        </div>
        <div className="text-[10px] text-slate-400">Asia/Kolkata Standard</div>
      </div>
    </aside>
  );
};
