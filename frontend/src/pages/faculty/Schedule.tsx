import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { appointmentsApi } from '../../api/appointments';
import { Appointment } from '../../types';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import { Textarea } from '../../components/ui/Input';
import { EmptyState } from '../../components/ui/EmptyState';
import { CardSkeleton } from '../../components/ui/Skeleton';
import { formatDate, formatTimeRange } from '../../utils/formatters';
import {
  Calendar,
  Clock,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';

export const FacultySchedule: React.FC = () => {
  const queryClient = useQueryClient();
  const [filterDate, setFilterDate] = useState<string>('');
  const [cancellingAppt, setCancellingAppt] = useState<Appointment | null>(null);
  const [cancelReason, setCancelReason] = useState('');
  const [actionError, setActionError] = useState<string | null>(null);

  const { data: appointments = [], isLoading } = useQuery({
    queryKey: ['my-appointments', filterDate],
    queryFn: () => appointmentsApi.listMyAppointments(filterDate ? { date: filterDate } : undefined),
  });

  const confirmedAppointments = appointments.filter(
    (a) => a.status === 'ACCEPTED' || a.status === 'COMPLETED'
  );

  const completeMutation = useMutation({
    mutationFn: (id: string) => appointmentsApi.completeAppointment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-appointments'] });
      setActionError(null);
    },
    onError: (err: any) => {
      setActionError(err.message || 'Cannot mark as completed before appointment end time.');
    },
  });

  const cancelMutation = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      appointmentsApi.cancelAppointment(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-appointments'] });
      setCancellingAppt(null);
      setCancelReason('');
      setActionError(null);
    },
    onError: (err: any) => {
      setActionError(err.message || 'Failed to cancel appointment.');
    },
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Faculty Schedule</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Confirmed student consultations and office hours agenda.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="date"
            value={filterDate}
            onChange={(e) => setFilterDate(e.target.value)}
            className="text-xs px-3 py-2 rounded-lg border border-slate-300 bg-white font-medium text-slate-700 focus:ring-2 focus:ring-brand-500"
          />
          {filterDate && (
            <Button variant="ghost" size="sm" onClick={() => setFilterDate('')}>
              Clear Date Filter
            </Button>
          )}
        </div>
      </div>

      {actionError && (
        <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{actionError}</span>
        </div>
      )}

      {/* Schedule Items List */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-5 space-y-3">
              <CardSkeleton />
              <CardSkeleton />
            </div>
          ) : confirmedAppointments.length === 0 ? (
            <div className="p-8">
              <EmptyState
                icon={<Calendar className="w-8 h-8 text-slate-400" />}
                title="No Confirmed Appointments"
                description={
                  filterDate
                    ? `No appointments found on ${formatDate(filterDate)}.`
                    : 'You have no upcoming confirmed student appointments scheduled.'
                }
              />
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {confirmedAppointments.map((appt) => (
                <div
                  key={appt.id}
                  className="p-5 hover:bg-slate-50/70 transition flex flex-col lg:flex-row lg:items-center justify-between gap-5"
                >
                  {/* Student & Reason */}
                  <div className="space-y-2.5 flex-1">
                    <div className="flex flex-wrap items-center gap-2.5">
                      <span className="text-sm font-bold text-slate-900">
                        {appt.student?.full_name}
                      </span>
                      <span className="text-xs text-slate-500">
                        ({appt.student?.major} · ID: {appt.student?.student_id_number})
                      </span>
                      <Badge size="sm" status={appt.status} />
                    </div>

                    <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-xs text-slate-800 space-y-1">
                      <p className="font-bold text-slate-900">Consultation Agenda:</p>
                      <p className="text-slate-700 leading-relaxed">{appt.reason}</p>
                    </div>

                    {appt.faculty_notes && (
                      <div className="bg-emerald-50/70 p-2.5 rounded-lg border border-emerald-200/60 text-xs text-emerald-900">
                        <span className="font-semibold">Your Notes: </span>
                        {appt.faculty_notes}
                      </div>
                    )}
                  </div>

                  {/* Date & Quick Lifecycle Actions */}
                  <div className="flex flex-col lg:items-end gap-3 shrink-0">
                    <div className="bg-brand-50/60 p-3 rounded-xl border border-brand-200/80 text-left lg:text-right space-y-1">
                      <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900">
                        <Calendar className="w-3.5 h-3.5 text-brand-600" />
                        <span>{formatDate(appt.date)}</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-xs font-bold text-brand-700">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{formatTimeRange(appt.start_time, appt.end_time)} IST</span>
                      </div>
                    </div>

                    {appt.status === 'ACCEPTED' && (
                      <div className="flex items-center gap-2 pt-1">
                        <Button
                          size="sm"
                          variant="success"
                          leftIcon={<CheckCircle2 className="w-3.5 h-3.5" />}
                          onClick={() => completeMutation.mutate(appt.id)}
                          isLoading={completeMutation.isPending}
                        >
                          Mark Completed
                        </Button>
                        <Button
                          size="sm"
                          variant="danger"
                          onClick={() => {
                            setCancellingAppt(appt);
                            setCancelReason('');
                            setActionError(null);
                          }}
                        >
                          Cancel
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Cancel Modal */}
      {cancellingAppt && (
        <Modal
          isOpen={!!cancellingAppt}
          onClose={() => setCancellingAppt(null)}
          title="Cancel Scheduled Appointment"
          description="Cancel this confirmed appointment. The student will be notified."
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              cancelMutation.mutate({ id: cancellingAppt.id, reason: cancelReason });
            }}
            className="space-y-4"
          >
            <div className="p-3 bg-slate-50 rounded-xl text-xs space-y-1 border border-slate-200">
              <p className="font-bold text-slate-900">{cancellingAppt.student?.full_name}</p>
              <p className="text-slate-600">
                {formatDate(cancellingAppt.date)} at{' '}
                {formatTimeRange(cancellingAppt.start_time, cancellingAppt.end_time)} IST
              </p>
            </div>

            <Textarea
              label="Reason for Cancellation"
              placeholder="E.g., Unexpected faculty committee commitment..."
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
                Back
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
