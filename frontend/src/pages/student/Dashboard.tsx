import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../context/AuthContext';
import { appointmentsApi } from '../../api/appointments';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { EmptyState } from '../../components/ui/EmptyState';
import { CardSkeleton } from '../../components/ui/Skeleton';
import { formatDate, formatTimeRange } from '../../utils/formatters';
import {
  Users,
  CalendarRange,
  Clock,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  Building2,
} from 'lucide-react';

export const StudentDashboard: React.FC = () => {
  const { user } = useAuth();

  const { data: appointments = [], isLoading } = useQuery({
    queryKey: ['my-appointments'],
    queryFn: () => appointmentsApi.listMyAppointments(),
  });

  const pendingAppointments = appointments.filter((a) => a.status === 'REQUESTED');
  const acceptedAppointments = appointments.filter((a) => a.status === 'ACCEPTED');
  const upcomingAppointment = acceptedAppointments[0] || pendingAppointments[0];

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-brand-900 to-slate-900 text-white rounded-2xl p-6 sm:p-8 shadow-sm relative overflow-hidden">
        <div className="relative z-10 max-w-2xl space-y-2">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-brand-500/20 text-brand-300 text-xs font-semibold border border-brand-400/30">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Student Academic Portal</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Welcome back, {user?.full_name}
          </h1>
          <p className="text-xs sm:text-sm text-slate-300">
            {user?.student_profile?.major} · ID: {user?.student_profile?.student_id_number}
          </p>
        </div>
      </div>

      {/* Quick Action Cards / Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="border-l-4 border-l-brand-600">
          <CardContent className="p-5 flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Confirmed Meetings
              </p>
              <p className="text-2xl font-bold text-slate-900">{acceptedAppointments.length}</p>
            </div>
            <div className="w-11 h-11 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-amber-500">
          <CardContent className="p-5 flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Pending Requests
              </p>
              <p className="text-2xl font-bold text-slate-900">{pendingAppointments.length}</p>
            </div>
            <div className="w-11 h-11 bg-amber-50 text-amber-600 rounded-xl flex items-center justify-center">
              <Clock className="w-6 h-6" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-slate-600 bg-slate-50/50">
          <CardContent className="p-5 flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Browse Directory
              </p>
              <Link
                to="/student/faculty"
                className="text-xs font-bold text-brand-600 hover:text-brand-700 inline-flex items-center gap-1 mt-1"
              >
                Find Faculty Members <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
            <div className="w-11 h-11 bg-brand-50 text-brand-600 rounded-xl flex items-center justify-center">
              <Users className="w-6 h-6" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Next Upcoming Appointment Highlight */}
      {upcomingAppointment && (
        <Card className="bg-brand-50/40 border-brand-200/80">
          <CardHeader className="pb-2 border-b border-brand-100 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-bold text-brand-900 flex items-center gap-2">
              <Clock className="w-4 h-4 text-brand-600" />
              Next Scheduled Appointment
            </CardTitle>
            <Badge status={upcomingAppointment.status} />
          </CardHeader>
          <CardContent className="p-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1.5">
                <h4 className="text-base font-bold text-slate-900">
                  {upcomingAppointment.faculty?.full_name}
                </h4>
                <p className="text-xs text-slate-600 flex items-center gap-2">
                  <Building2 className="w-3.5 h-3.5 text-slate-400" />
                  <span>
                    {upcomingAppointment.faculty?.title} · {upcomingAppointment.faculty?.office_location}
                  </span>
                </p>
                <p className="text-xs text-slate-700 italic bg-white/80 p-2.5 rounded-lg border border-brand-100/60 max-w-xl">
                  "{upcomingAppointment.reason}"
                </p>
              </div>

              <div className="text-left sm:text-right shrink-0 space-y-1">
                <p className="text-sm font-bold text-brand-900">
                  {formatDate(upcomingAppointment.date)}
                </p>
                <p className="text-xs font-semibold text-brand-700 bg-brand-100/70 px-2.5 py-1 rounded-md inline-block">
                  {formatTimeRange(upcomingAppointment.start_time, upcomingAppointment.end_time)} IST
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Appointments */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Recent Activity</CardTitle>
            <p className="text-xs text-slate-500 mt-0.5">Your recent appointment booking requests</p>
          </div>
          <Link to="/student/appointments">
            <Button variant="outline" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
              View All
            </Button>
          </Link>
        </CardHeader>

        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-5 space-y-3">
              <CardSkeleton />
              <CardSkeleton />
            </div>
          ) : appointments.length === 0 ? (
            <div className="p-8">
              <EmptyState
                icon={<CalendarRange className="w-6 h-6 text-slate-400" />}
                title="No Appointments Yet"
                description="Browse available faculty members to schedule an academic meeting or consultation."
                actionLabel="Find Faculty"
                onAction={() => window.location.assign('/student/faculty')}
              />
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {appointments.slice(0, 5).map((appt) => (
                <div
                  key={appt.id}
                  className="p-4 sm:p-5 hover:bg-slate-50/80 transition flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-slate-900">
                        {appt.faculty?.full_name || 'Faculty Member'}
                      </span>
                      <Badge size="sm" status={appt.status} />
                    </div>
                    <p className="text-xs text-slate-500 line-clamp-1">{appt.reason}</p>
                  </div>

                  <div className="flex items-center justify-between sm:justify-end gap-3 text-xs">
                    <span className="font-medium text-slate-600">
                      {formatDate(appt.date)} · {formatTimeRange(appt.start_time, appt.end_time)}
                    </span>
                    <Link
                      to={`/student/appointments/${appt.id}`}
                      className="text-brand-600 hover:text-brand-700 font-semibold p-1"
                    >
                      Details →
                    </Link>
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
