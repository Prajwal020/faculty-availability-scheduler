import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { appointmentsApi } from '../../api/appointments';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import { Textarea } from '../../components/ui/Input';
import { EmptyState } from '../../components/ui/EmptyState';
import { CardSkeleton } from '../../components/ui/Skeleton';
import { formatDate, formatTimeRange } from '../../utils/formatters';
import {
  ArrowLeft,
  Calendar,
  Clock,
  Building2,
  MapPin,
  AlertCircle,
} from 'lucide-react';

export const StudentAppointmentDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [isCancelModalOpen, setIsCancelModalOpen] = useState(false);
  const [cancelReason, setCancelReason] = useState('');
  const [cancelError, setCancelError] = useState<string | null>(null);

  const { data: appt, isLoading } = useQuery({
    queryKey: ['appointment-details', id],
    queryFn: () => appointmentsApi.getAppointmentDetails(id!),
    enabled: !!id,
  });

  const cancelMutation = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      appointmentsApi.cancelAppointment(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointment-details', id] });
      queryClient.invalidateQueries({ queryKey: ['my-appointments'] });
      setIsCancelModalOpen(false);
      setCancelReason('');
    },
    onError: (err: any) => {
      setCancelError(err.message || 'Failed to cancel appointment.');
    },
  });

  if (isLoading) return <CardSkeleton />;

  if (!appt) {
    return (
      <EmptyState
        title="Appointment Not Found"
        description="The requested appointment details could not be found."
        actionLabel="Back to Appointments"
        onAction={() => navigate('/student/appointments')}
      />
    );
  }

  const canCancel = appt.status === 'REQUESTED' || appt.status === 'ACCEPTED';

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Back button */}
      <Link
        to="/student/appointments"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition"
      >
        <ArrowLeft className="w-4 h-4" /> Back to My Appointments
      </Link>

      <Card className="shadow-sm">
        <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-50/50">
          <div>
            <div className="flex items-center gap-2.5">
              <CardTitle>Appointment Details</CardTitle>
              <Badge status={appt.status} />
            </div>
            <p className="text-xs text-slate-500 mt-0.5">Booking ID: {appt.id}</p>
          </div>

          {canCancel && (
            <Button
              variant="danger"
              size="sm"
              onClick={() => {
                setIsCancelModalOpen(true);
                setCancelError(null);
              }}
            >
              Cancel Appointment
            </Button>
          )}
        </CardHeader>

        <CardContent className="p-6 space-y-6">
          {/* Timing Banner */}
          <div className="p-4 bg-brand-50/60 rounded-xl border border-brand-200/70 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-brand-600 text-white rounded-xl flex items-center justify-center font-bold">
                <Calendar className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs text-brand-800 font-semibold">Scheduled Date</p>
                <p className="text-sm font-bold text-slate-900">{formatDate(appt.date)}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-brand-900 font-bold bg-white px-3 py-1.5 rounded-lg border border-brand-200 text-xs">
              <Clock className="w-4 h-4 text-brand-600" />
              <span>{formatTimeRange(appt.start_time, appt.end_time)} (Asia/Kolkata IST)</span>
            </div>
          </div>

          {/* Faculty Profile Card */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Faculty Advisor
            </h4>
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-brand-100 border border-brand-200 text-brand-700 font-bold flex items-center justify-center">
                  {appt.faculty?.full_name?.charAt(0) || 'F'}
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">{appt.faculty?.full_name}</h3>
                  <p className="text-xs text-brand-700 font-medium">{appt.faculty?.title}</p>
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-600 pt-2 border-t border-slate-200/60">
                <div className="flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-slate-400" />
                  <span>{appt.faculty?.department_name || 'Department'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-slate-400" />
                  <span>Office: {appt.faculty?.office_location}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Agenda & Notes */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Agenda & Communication
            </h4>
            <div className="space-y-2.5">
              <div className="p-3.5 rounded-xl border border-slate-200 bg-white">
                <p className="text-xs font-bold text-slate-800 mb-1">Student Purpose / Agenda:</p>
                <p className="text-xs text-slate-600 leading-relaxed">{appt.reason}</p>
              </div>

              {appt.faculty_notes && (
                <div className="p-3.5 rounded-xl border border-emerald-200 bg-emerald-50/60 text-xs text-emerald-900">
                  <p className="font-bold text-emerald-800 mb-1">Faculty Note / Preparation:</p>
                  <p className="leading-relaxed">{appt.faculty_notes}</p>
                </div>
              )}

              {appt.cancellation_reason && (
                <div className="p-3.5 rounded-xl border border-red-200 bg-red-50/60 text-xs text-red-900">
                  <p className="font-bold text-red-800 mb-1">Cancellation / Rejection Reason:</p>
                  <p className="leading-relaxed">{appt.cancellation_reason}</p>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Cancel Modal */}
      <Modal
        isOpen={isCancelModalOpen}
        onClose={() => setIsCancelModalOpen(false)}
        title="Cancel Appointment"
        description="Are you sure you want to cancel this scheduled appointment?"
      >
        <form
          onSubmit={(e) => {
            e.preventDefault();
            cancelMutation.mutate({ id: appt.id, reason: cancelReason });
          }}
          className="space-y-4"
        >
          {cancelError && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{cancelError}</span>
            </div>
          )}

          <Textarea
            label="Reason for cancellation (optional)"
            placeholder="Provide context..."
            value={cancelReason}
            onChange={(e) => setCancelReason(e.target.value)}
            rows={2}
          />

          <div className="flex justify-end gap-2.5 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsCancelModalOpen(false)}
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
    </div>
  );
};
