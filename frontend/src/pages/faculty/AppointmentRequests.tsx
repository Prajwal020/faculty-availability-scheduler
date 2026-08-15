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
  XCircle,
  AlertCircle,
  Mail,
} from 'lucide-react';

export const FacultyAppointmentRequests: React.FC = () => {
  const queryClient = useQueryClient();
  const [acceptingAppt, setAcceptingAppt] = useState<Appointment | null>(null);
  const [rejectingAppt, setRejectingAppt] = useState<Appointment | null>(null);
  const [notes, setNotes] = useState('');
  const [rejectReason, setRejectReason] = useState('');
  const [actionError, setActionError] = useState<string | null>(null);

  const { data: appointments = [], isLoading } = useQuery({
    queryKey: ['my-appointments'],
    queryFn: () => appointmentsApi.listMyAppointments(),
  });

  const pendingRequests = appointments.filter((a) => a.status === 'REQUESTED');

  const acceptMutation = useMutation({
    mutationFn: ({ id, notes }: { id: string; notes?: string }) =>
      appointmentsApi.acceptAppointment(id, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-appointments'] });
      setAcceptingAppt(null);
      setNotes('');
      setActionError(null);
    },
    onError: (err: any) => {
      setActionError(err.message || 'Failed to accept appointment request.');
    },
  });

  const rejectMutation = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      appointmentsApi.rejectAppointment(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-appointments'] });
      setRejectingAppt(null);
      setRejectReason('');
      setActionError(null);
    },
    onError: (err: any) => {
      setActionError(err.message || 'Failed to reject appointment request.');
    },
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          Appointment Requests ({pendingRequests.length})
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Review pending meeting requests from students. Accepted requests lock the calendar slot.
        </p>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-5 space-y-3">
              <CardSkeleton />
              <CardSkeleton />
            </div>
          ) : pendingRequests.length === 0 ? (
            <div className="p-8">
              <EmptyState
                icon={<CheckCircle2 className="w-8 h-8 text-emerald-500" />}
                title="All Caught Up!"
                description="You have no pending appointment requests at this moment."
              />
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {pendingRequests.map((appt) => (
                <div
                  key={appt.id}
                  className="p-5 hover:bg-slate-50/70 transition flex flex-col lg:flex-row lg:items-center justify-between gap-5"
                >
                  {/* Student Details & Agenda */}
                  <div className="space-y-3 flex-1">
                    <div className="flex flex-wrap items-center gap-2.5">
                      <div className="w-8 h-8 rounded-lg bg-brand-100 border border-brand-200 text-brand-700 font-bold text-xs flex items-center justify-center">
                        {appt.student?.full_name?.charAt(0) || 'S'}
                      </div>
                      <span className="text-sm font-bold text-slate-900">
                        {appt.student?.full_name}
                      </span>
                      <span className="text-xs text-slate-500 font-medium">
                        ({appt.student?.major} · ID: {appt.student?.student_id_number})
                      </span>
                      <Badge size="sm" status={appt.status} />
                    </div>

                    <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-xs text-slate-800 space-y-1">
                      <p className="font-bold text-slate-900">Requested Agenda:</p>
                      <p className="leading-relaxed text-slate-700">{appt.reason}</p>
                    </div>

                    <div className="flex items-center gap-3 text-xs text-slate-500">
                      <span className="flex items-center gap-1">
                        <Mail className="w-3.5 h-3.5 text-slate-400" />
                        {appt.student?.email}
                      </span>
                    </div>
                  </div>

                  {/* Requested Time & Action Buttons */}
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

                    <div className="flex items-center gap-2 pt-1">
                      <Button
                        size="sm"
                        variant="success"
                        leftIcon={<CheckCircle2 className="w-4 h-4" />}
                        onClick={() => {
                          setAcceptingAppt(appt);
                          setNotes('');
                          setActionError(null);
                        }}
                      >
                        Accept
                      </Button>
                      <Button
                        size="sm"
                        variant="danger"
                        leftIcon={<XCircle className="w-4 h-4" />}
                        onClick={() => {
                          setRejectingAppt(appt);
                          setRejectReason('');
                          setActionError(null);
                        }}
                      >
                        Reject
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Accept Modal */}
      {acceptingAppt && (
        <Modal
          isOpen={!!acceptingAppt}
          onClose={() => setAcceptingAppt(null)}
          title="Accept Appointment Request"
          description="Confirm this meeting with the student. You may attach optional instructions or preparation notes."
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              acceptMutation.mutate({ id: acceptingAppt.id, notes });
            }}
            className="space-y-4"
          >
            {actionError && (
              <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{actionError}</span>
              </div>
            )}

            <div className="p-3 bg-slate-50 rounded-xl text-xs space-y-1 border border-slate-200">
              <p className="font-bold text-slate-900">{acceptingAppt.student?.full_name}</p>
              <p className="text-slate-600">
                {formatDate(acceptingAppt.date)} at{' '}
                {formatTimeRange(acceptingAppt.start_time, acceptingAppt.end_time)} IST
              </p>
            </div>

            <Textarea
              label="Optional Notes for Student"
              placeholder="E.g., Please bring your chapter 3 draft and lab test logs..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={2}
            />

            <div className="flex justify-end gap-2.5 pt-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setAcceptingAppt(null)}
                disabled={acceptMutation.isPending}
              >
                Cancel
              </Button>
              <Button type="submit" variant="success" isLoading={acceptMutation.isPending}>
                Confirm & Accept
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* Reject Modal */}
      {rejectingAppt && (
        <Modal
          isOpen={!!rejectingAppt}
          onClose={() => setRejectingAppt(null)}
          title="Decline Appointment Request"
          description="Decline this meeting request. The student will be notified and this slot will be released."
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              rejectMutation.mutate({ id: rejectingAppt.id, reason: rejectReason });
            }}
            className="space-y-4"
          >
            {actionError && (
              <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{actionError}</span>
              </div>
            )}

            <div className="p-3 bg-slate-50 rounded-xl text-xs space-y-1 border border-slate-200">
              <p className="font-bold text-slate-900">{rejectingAppt.student?.full_name}</p>
              <p className="text-slate-600">
                {formatDate(rejectingAppt.date)} at{' '}
                {formatTimeRange(rejectingAppt.start_time, rejectingAppt.end_time)} IST
              </p>
            </div>

            <Textarea
              label="Reason for Declining (optional)"
              placeholder="E.g., Urgent departmental seminar conflict, please reschedule for Wednesday..."
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              rows={2}
            />

            <div className="flex justify-end gap-2.5 pt-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setRejectingAppt(null)}
                disabled={rejectMutation.isPending}
              >
                Back
              </Button>
              <Button type="submit" variant="danger" isLoading={rejectMutation.isPending}>
                Decline Request
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};
