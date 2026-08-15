import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { appointmentsApi } from '../../api/appointments';
import { Appointment } from '../../types';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Tabs } from '../../components/ui/Tabs';
import { Modal } from '../../components/ui/Modal';
import { Textarea } from '../../components/ui/Input';
import { EmptyState } from '../../components/ui/EmptyState';
import { CardSkeleton } from '../../components/ui/Skeleton';
import { formatDate, formatTimeRange } from '../../utils/formatters';
import {
  CalendarRange,
  Building2,
  AlertCircle,
  ArrowRight,
} from 'lucide-react';

export const StudentAppointmentsList: React.FC = () => {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<string>('ALL');
  const [cancellingAppt, setCancellingAppt] = useState<Appointment | null>(null);
  const [cancelReason, setCancelReason] = useState<string>('');
  const [cancelError, setCancelError] = useState<string | null>(null);

  const { data: appointments = [], isLoading } = useQuery({
    queryKey: ['my-appointments'],
    queryFn: () => appointmentsApi.listMyAppointments(),
  });

  const cancelMutation = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      appointmentsApi.cancelAppointment(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-appointments'] });
      setCancellingAppt(null);
      setCancelReason('');
      setCancelError(null);
    },
    onError: (err: any) => {
      setCancelError(err.message || 'Failed to cancel appointment.');
    },
  });

  const handleCancelSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!cancellingAppt) return;
    cancelMutation.mutate({ id: cancellingAppt.id, reason: cancelReason });
  };

  const filteredAppointments = appointments.filter((appt) => {
    if (activeTab === 'ALL') return true;
    if (activeTab === 'ACCEPTED') return appt.status === 'ACCEPTED';
    if (activeTab === 'REQUESTED') return appt.status === 'REQUESTED';
    if (activeTab === 'COMPLETED') return appt.status === 'COMPLETED';
    if (activeTab === 'CANCELLED')
      return appt.status === 'CANCELLED' || appt.status === 'REJECTED';
    return true;
  });

  const counts = {
    all: appointments.length,
    accepted: appointments.filter((a) => a.status === 'ACCEPTED').length,
    requested: appointments.filter((a) => a.status === 'REQUESTED').length,
    completed: appointments.filter((a) => a.status === 'COMPLETED').length,
    cancelled: appointments.filter((a) => a.status === 'CANCELLED' || a.status === 'REJECTED').length,
  };

  const tabs = [
    { id: 'ALL', label: 'All Appointments', count: counts.all },
    { id: 'ACCEPTED', label: 'Confirmed', count: counts.accepted },
    { id: 'REQUESTED', label: 'Pending Requests', count: counts.requested },
    { id: 'COMPLETED', label: 'Completed', count: counts.completed },
    { id: 'CANCELLED', label: 'Cancelled / Rejected', count: counts.cancelled },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">My Appointments</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Track, review, or cancel your scheduled faculty meetings.
          </p>
        </div>
        <Link to="/student/faculty">
          <Button rightIcon={<ArrowRight className="w-4 h-4" />}>Book New Appointment</Button>
        </Link>
      </div>

      {/* Tabs Filter */}
      <Card>
        <div className="px-5 pt-3">
          <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />
        </div>

        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-5 space-y-3">
              <CardSkeleton />
              <CardSkeleton />
            </div>
          ) : filteredAppointments.length === 0 ? (
            <div className="p-8">
              <EmptyState
                icon={<CalendarRange className="w-6 h-6 text-slate-400" />}
                title="No Appointments Found"
                description="No appointment records match the selected status category."
              />
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {filteredAppointments.map((appt) => {
                const canCancel = appt.status === 'REQUESTED' || appt.status === 'ACCEPTED';
                return (
                  <div
                    key={appt.id}
                    className="p-5 hover:bg-slate-50/70 transition flex flex-col md:flex-row md:items-center justify-between gap-4"
                  >
                    {/* Faculty & Agenda Info */}
                    <div className="space-y-2 max-w-xl">
                      <div className="flex flex-wrap items-center gap-2.5">
                        <h3 className="text-sm font-bold text-slate-900">
                          {appt.faculty?.full_name}
                        </h3>
                        <Badge size="sm" status={appt.status} />
                      </div>

                      <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600">
                        <span className="flex items-center gap-1">
                          <Building2 className="w-3.5 h-3.5 text-slate-400" />
                          {appt.faculty?.department_name || 'Academic Dept'}
                        </span>
                        <span>·</span>
                        <span>Office: {appt.faculty?.office_location}</span>
                      </div>

                      <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200/60 text-xs text-slate-700">
                        <span className="font-semibold text-slate-900">Purpose: </span>
                        {appt.reason}
                      </div>

                      {appt.faculty_notes && (
                        <div className="bg-emerald-50/70 p-2 rounded-lg border border-emerald-200/60 text-xs text-emerald-800">
                          <span className="font-semibold">Faculty Note: </span>
                          {appt.faculty_notes}
                        </div>
                      )}

                      {appt.cancellation_reason && (
                        <div className="bg-red-50/70 p-2 rounded-lg border border-red-200/60 text-xs text-red-800">
                          <span className="font-semibold">Cancellation Reason: </span>
                          {appt.cancellation_reason}
                        </div>
                      )}
                    </div>

                    {/* Schedule & Actions */}
                    <div className="flex flex-col md:items-end gap-3 shrink-0">
                      <div className="text-left md:text-right space-y-1">
                        <p className="text-xs font-bold text-slate-900">
                          {formatDate(appt.date)}
                        </p>
                        <p className="text-xs font-semibold text-brand-700 bg-brand-50 px-2 py-0.5 rounded border border-brand-200 inline-block">
                          {formatTimeRange(appt.start_time, appt.end_time)} IST
                        </p>
                      </div>

                      <div className="flex items-center gap-2 pt-1">
                        <Link to={`/student/appointments/${appt.id}`}>
                          <Button variant="outline" size="sm">
                            View Details
                          </Button>
                        </Link>
                        {canCancel && (
                          <Button
                            variant="danger"
                            size="sm"
                            onClick={() => {
                              setCancellingAppt(appt);
                              setCancelReason('');
                              setCancelError(null);
                            }}
                          >
                            Cancel
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Cancel Confirmation Modal */}
      {cancellingAppt && (
        <Modal
          isOpen={!!cancellingAppt}
          onClose={() => setCancellingAppt(null)}
          title="Cancel Appointment Request"
          description="Are you sure you want to cancel this appointment? This action will free up the faculty member's slot."
        >
          <form onSubmit={handleCancelSubmit} className="space-y-4">
            {cancelError && (
              <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{cancelError}</span>
              </div>
            )}

            <div className="p-3 bg-slate-50 rounded-lg text-xs space-y-1 border border-slate-200">
              <p className="font-bold text-slate-900">{cancellingAppt.faculty?.full_name}</p>
              <p className="text-slate-600">
                {formatDate(cancellingAppt.date)} at{' '}
                {formatTimeRange(cancellingAppt.start_time, cancellingAppt.end_time)} IST
              </p>
            </div>

            <Textarea
              label="Reason for cancellation (optional)"
              placeholder="E.g., Schedule conflict, resolved question during lecture..."
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
              rows={2}
            />

            <div className="flex justify-end gap-2.5 pt-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setCancellingAppt(null)}
                disabled={cancelMutation.isPending}
              >
                Keep Appointment
              </Button>
              <Button type="submit" variant="danger" isLoading={cancelMutation.isPending}>
                Confirm Cancellation
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};
