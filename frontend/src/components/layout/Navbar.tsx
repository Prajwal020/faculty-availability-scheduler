import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Badge } from '../ui/Badge';
import {
  Menu,
  LogOut,
  User as UserIcon,
  ChevronDown,
  Clock,
} from 'lucide-react';

interface NavbarProps {
  onToggleMobile: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleMobile }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getSubtext = () => {
    if (user?.role === 'STUDENT' && user.student_profile) {
      return `${user.student_profile.major} · ${user.student_profile.student_id_number}`;
    }
    if (user?.role === 'FACULTY' && user.faculty_profile) {
      return `${user.faculty_profile.title} · ${user.faculty_profile.office_location}`;
    }
    return user?.email;
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200/80 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30 shadow-2xs">
      {/* Left: Mobile menu toggle */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleMobile}
          className="lg:hidden p-2 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-slate-100 transition"
          aria-label="Toggle navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Institution Badge */}
        <div className="hidden sm:flex items-center gap-2 text-xs text-slate-500 font-medium bg-slate-50 border border-slate-200/60 px-3 py-1.5 rounded-full">
          <Clock className="w-3.5 h-3.5 text-brand-600" />
          <span>Institution Time:</span>
          <span className="font-semibold text-slate-700">Asia/Kolkata (IST)</span>
        </div>
      </div>

      {/* Right: User menu */}
      <div className="flex items-center gap-3" ref={dropdownRef}>
        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-3 p-1.5 rounded-xl hover:bg-slate-100 transition text-left focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <div className="w-9 h-9 rounded-xl bg-brand-100 border border-brand-200 text-brand-700 font-bold text-sm flex items-center justify-center shadow-2xs">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div className="hidden md:block">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-900 leading-none">
                  {user?.full_name}
                </span>
                <Badge size="sm" status={user?.role} showIcon={false} />
              </div>
              <p className="text-[11px] text-slate-500 truncate max-w-[180px] mt-0.5">
                {getSubtext()}
              </p>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </button>

          {/* Dropdown Menu */}
          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl border border-slate-200 shadow-lg py-1.5 z-50 animate-in fade-in-80 duration-150">
              <div className="px-4 py-2 border-b border-slate-100">
                <p className="text-xs font-bold text-slate-900">{user?.full_name}</p>
                <p className="text-[11px] text-slate-500 truncate">{user?.email}</p>
              </div>

              <Link
                to="/profile"
                onClick={() => setDropdownOpen(false)}
                className="flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition"
              >
                <UserIcon className="w-4 h-4 text-slate-400" />
                <span>My Profile</span>
              </Link>

              <div className="border-t border-slate-100 my-1"></div>

              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-red-600 hover:bg-red-50 transition text-left"
              >
                <LogOut className="w-4 h-4" />
                <span>Sign Out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
