import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { usersApi } from '../../api/users';
import { departmentsApi } from '../../api/departments';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { CardSkeleton } from '../../components/ui/Skeleton';
import {
  Shield,
  Users,
  GraduationCap,
  Building2,
  ArrowRight,
  School,
} from 'lucide-react';

export const AdminDashboard: React.FC = () => {
  const { data: users = [], isLoading: isUsersLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => usersApi.listUsersAdmin(0, 100),
  });

  const { data: departments = [] } = useQuery({
    queryKey: ['departments'],
    queryFn: () => departmentsApi.listDepartments(),
  });

  const studentCount = users.filter((u) => u.role === 'STUDENT').length;
  const facultyCount = users.filter((u) => u.role === 'FACULTY').length;
  const activeUserCount = users.filter((u) => u.status === 'ACTIVE').length;

  return (
    <div className="space-y-6">
      {/* Admin Banner */}
      <div className="bg-gradient-to-r from-slate-950 via-slate-900 to-brand-950 text-white rounded-2xl p-6 sm:p-8 shadow-sm relative overflow-hidden">
        <div className="relative z-10 max-w-2xl space-y-2">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-brand-500/20 text-brand-300 text-xs font-semibold border border-brand-400/30">
            <Shield className="w-3.5 h-3.5" />
            <span>Institution Administration Console</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Institutional Overview & Control
          </h1>
          <p className="text-xs sm:text-sm text-slate-300">
            Manage academic departments, faculty profiles, and user accounts across the institution.
          </p>
        </div>
      </div>

      {/* Institutional Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-l-4 border-l-brand-600">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                Total Users
              </p>
              <p className="text-2xl font-bold text-slate-900 mt-1">{users.length}</p>
              <p className="text-[10px] text-emerald-600 font-semibold mt-0.5">
                {activeUserCount} Active
              </p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center">
              <Users className="w-5 h-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-emerald-600">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                Faculty Members
              </p>
              <p className="text-2xl font-bold text-slate-900 mt-1">{facultyCount}</p>
              <p className="text-[10px] text-slate-500 mt-0.5">Teaching & Advisory</p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <GraduationCap className="w-5 h-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-amber-500">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                Enrolled Students
              </p>
              <p className="text-2xl font-bold text-slate-900 mt-1">{studentCount}</p>
              <p className="text-[10px] text-slate-500 mt-0.5">Undergrad / Postgrad</p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <School className="w-5 h-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-600">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                Academic Depts
              </p>
              <p className="text-2xl font-bold text-slate-900 mt-1">{departments.length}</p>
              <p className="text-[10px] text-slate-500 mt-0.5">Active Divisions</p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
              <Building2 className="w-5 h-5" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Navigation Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Link to="/admin/faculty" className="block group">
          <Card className="h-full group-hover:border-brand-500 transition">
            <CardContent className="p-5 space-y-2">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                <GraduationCap className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 group-hover:text-brand-600 transition">
                Faculty Management
              </h3>
              <p className="text-xs text-slate-500">
                View faculty profiles, department associations, office locations, and meeting modes.
              </p>
            </CardContent>
          </Card>
        </Link>

        <Link to="/admin/users" className="block group">
          <Card className="h-full group-hover:border-brand-500 transition">
            <CardContent className="p-5 space-y-2">
              <div className="w-10 h-10 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center">
                <Users className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 group-hover:text-brand-600 transition">
                User Management
              </h3>
              <p className="text-xs text-slate-500">
                Activate or deactivate user accounts, manage role permissions, and register new members.
              </p>
            </CardContent>
          </Card>
        </Link>

        <Link to="/admin/departments" className="block group">
          <Card className="h-full group-hover:border-brand-500 transition">
            <CardContent className="p-5 space-y-2">
              <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
                <Building2 className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 group-hover:text-brand-600 transition">
                Department Management
              </h3>
              <p className="text-xs text-slate-500">
                Create and organize academic departments, department codes, and campus building allocations.
              </p>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Recent Users Table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>System Accounts</CardTitle>
            <p className="text-xs text-slate-500 mt-0.5">Recently active institutional users</p>
          </div>
          <Link to="/admin/users">
            <Button variant="outline" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
              Manage All Users
            </Button>
          </Link>
        </CardHeader>

        <CardContent className="p-0">
          {isUsersLoading ? (
            <div className="p-5 space-y-3">
              <CardSkeleton />
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {users.slice(0, 5).map((u) => (
                <div
                  key={u.id}
                  className="p-4 hover:bg-slate-50/70 transition flex items-center justify-between gap-4 text-xs"
                >
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-900">{u.full_name}</span>
                      <Badge size="sm" status={u.role} showIcon={false} />
                    </div>
                    <p className="text-slate-500">{u.email}</p>
                  </div>

                  <div>
                    <Badge size="sm" status={u.status} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
