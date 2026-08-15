import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../context/AuthContext';
import { appointmentsApi } from '../../api/appointments';
import { availabilityApi } from '../../api/availability';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { CardSkeleton } from '../../components/ui/Skeleton';
import { formatDate, formatTimeRange, getTodayDateString } from '../../utils/formatters';
import {
  Users,
  Calendar,
  Clock,
  UserCheck,
  Ban,
  ArrowRight,
  Sparkles,
} from 'lucide-react';

export const FacultyDashboard: React.FC = () => {
  const { user } = useAuth();
  const today = getTodayDateString();

  const { data: appointments = [], isLoading: isApptsLoading } = useQuery({
    queryKey: ['my-appointments'],
    queryFn: () => appointmentsApi.listMyAppointments(),
  });

  const { data: regularHours = [] } = useQuery({
    queryKey: ['my-regular-availability'],
    queryFn: () => availabilityApi.listRegular(),
  });

  const pendingRequests = appointments.filter((a) => a.status === 'REQUESTED');
  const acceptedAppointments = appointments.filter((a) => a.status === 'ACCEPTED');
  const todayAppointments = acceptedAppointments.filter((a) => a.date === today);

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-brand-950 to-slate-900 text-white rounded-2xl p-6 sm:p-8 shadow-sm relative overflow-hidden">
        <div className="relative z-10 max-w-2xl space-y-2">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-brand-500/20 text-brand-300 text-xs font-semibold border border-brand-400/30">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Faculty Advisor Portal</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Welcome, {user?.full_name}
          </h1>
          <p className="text-xs sm:text-sm text-slate-300">
            {user?.faculty_profile?.title} · Office: {user?.faculty_profile?.office_location}
          </p>
        </div>
      </div>

      {/* Pending Requests Alert Callout */}
      {pendingRequests.length > 0 && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500 text-white flex items-center justify-center font-bold shrink-0 shadow-xs">
              <UserCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-xs font-bold text-amber-950">
                You have {pendingRequests.length} pending appointment request(s)
              </h3>
              <p className="text-xs text-amber-800">
                Students are waiting for your review and confirmation.
              </p>
            </div>
          </div>
          <Link to="/faculty/requests">
            <Button size="sm" variant="primary" rightIcon={<ArrowRight className="w-4 h-4" />}>
              Review Requests ({pendingRequests.length})
            </Button>
          </Link>
        </div>
      )}

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <Card className="border-l-4 border-l-amber-500">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                Pending Requests
              </p>
              <p className="text-2xl font-bold text-slate-900 mt-1">{pendingRequests.length}</p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <Clock className="w-5 h-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-brand-600">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                Today's Meetings
              </p>
              <p className="text-2xl font-bold text-slate-900 mt-1">{todayAppointments.length}</p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center">
              <Calendar className="w-5 h-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-emerald-600">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                Confirmed Total
              </p>
              <p className="text-2xl font-bold text-slate-900 mt-1">
                {acceptedAppointments.length}
              </p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <UserCheck className="w-5 h-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-slate-700">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                Weekly Windows
              </p>
              <p className="text-2xl font-bold text-slate-900 mt-1">{regularHours.length}</p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center">
              <Clock className="w-5 h-5" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Today's Schedule & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Today's Appointments */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-sm font-bold flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-brand-600" />
                  Today's Schedule ({formatDate(today)})
                </CardTitle>
                <p className="text-xs text-slate-500 mt-0.5">
                  Confirmed student consultations for today
                </p>
              </div>
              <Link to="/faculty/schedule">
                <Button variant="outline" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                  Full Schedule
                </Button>
              </Link>
            </CardHeader>

            <CardContent className="p-0">
              {isApptsLoading ? (
                <div className="p-5 space-y-3">
                  <CardSkeleton />
                </div>
              ) : todayAppointments.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-500 space-y-1">
                  <p className="font-semibold text-slate-700">No appointments scheduled for today.</p>
                  <p>Your calendar is clear or you have no confirmed meetings today.</p>
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {todayAppointments.map((appt) => (
                    <div
                      key={appt.id}
                      className="p-4 hover:bg-slate-50/70 transition flex items-center justify-between gap-4"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-slate-900">
                            {appt.student?.full_name}
                          </span>
                          <span className="text-[11px] text-slate-500">
                            ({appt.student?.major} · ID: {appt.student?.student_id_number})
                          </span>
                        </div>
                        <p className="text-xs text-slate-600 line-clamp-1 italic">
                          "{appt.reason}"
                        </p>
                      </div>

                      <div className="text-right shrink-0">
                        <span className="text-xs font-bold text-brand-700 bg-brand-50 px-2 py-0.5 rounded border border-brand-200">
                          {formatTimeRange(appt.start_time, appt.end_time)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right 1 Col: Quick Management Actions */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-bold">Quick Availability Tools</CardTitle>
              <p className="text-xs text-slate-500 mt-0.5">Manage your dynamic schedule settings</p>
            </CardHeader>
            <CardContent className="p-4 space-y-2">
              <Link
                to="/faculty/availability"
                className="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:border-brand-500 hover:bg-brand-50/30 transition text-xs font-semibold text-slate-800"
              >
                <div className="flex items-center gap-2.5">
                  <Clock className="w-4 h-4 text-brand-600" />
                  <span>Weekly Office Hours</span>
                </div>
                <span className="text-slate-400">→</span>
              </Link>

              <Link
                to="/faculty/temporary"
                className="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:border-brand-500 hover:bg-brand-50/30 transition text-xs font-semibold text-slate-800"
              >
                <div className="flex items-center gap-2.5">
                  <Sparkles className="w-4 h-4 text-brand-600" />
                  <span>Pop-up Extra Hours</span>
                </div>
                <span className="text-slate-400">→</span>
              </Link>

              <Link
                to="/faculty/blocks"
                className="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:border-brand-500 hover:bg-brand-50/30 transition text-xs font-semibold text-slate-800"
              >
                <div className="flex items-center gap-2.5">
                  <Ban className="w-4 h-4 text-red-500" />
                  <span>Block Time Period</span>
                </div>
                <span className="text-slate-400">→</span>
              </Link>

              <Link
                to="/faculty/leave"
                className="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:border-brand-500 hover:bg-brand-50/30 transition text-xs font-semibold text-slate-800"
              >
                <div className="flex items-center gap-2.5">
                  <Users className="w-4 h-4 text-amber-500" />
                  <span>Declare Leave</span>
                </div>
                <span className="text-slate-400">→</span>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
