import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { appointmentsApi } from '../../api/appointments';
import { BookableSlot, FacultyPublicProfile } from '../../types';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Textarea } from '../ui/Input';
import { formatDate, formatTimeRange } from '../../utils/formatters';
import { Calendar, Clock, AlertCircle, CheckCircle2, User, Building2 } from 'lucide-react';

interface BookingModalProps {
  isOpen: boolean;
  onClose: () => void;
  faculty: FacultyPublicProfile;
  date: string;
  slot: BookableSlot | null;
  onSuccess?: () => void;
}

export const BookingModal: React.FC<BookingModalProps> = ({
  isOpen,
  onClose,
  faculty,
  date,
  slot,
  onSuccess,
}) => {
  const queryClient = useQueryClient();
  const [reason, setReason] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isBooked, setIsBooked] = useState(false);

  const mutation = useMutation({
    mutationFn: appointmentsApi.bookAppointment,
    onSuccess: () => {
      setIsBooked(true);
      queryClient.invalidateQueries({ queryKey: ['faculty-availability', faculty.id, date] });
      queryClient.invalidateQueries({ queryKey: ['my-appointments'] });
      if (onSuccess) onSuccess();
    },
    onError: (error: any) => {
      if (error.code === 'SLOT_UNAVAILABLE') {
        setErrorMessage(
          'This slot was just booked or is no longer available. Please select another time slot.'
        );
      } else {
        setErrorMessage(error.message || 'Failed to submit appointment request. Please try again.');
      }
    },
  });

  if (!slot) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!reason.trim()) {
      setErrorMessage('Please state the purpose or agenda for your appointment.');
      return;
    }

    setErrorMessage(null);
    mutation.mutate({
      faculty_id: faculty.id,
      date,
      start_time: `${slot.start_time}:00`,
      end_time: `${slot.end_time}:00`,
      reason: reason.trim(),
    });
  };

  const handleModalClose = () => {
    setReason('');
    setErrorMessage(null);
    setIsBooked(false);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleModalClose}
      title={isBooked ? 'Appointment Requested!' : 'Request Faculty Appointment'}
      description={
        isBooked
          ? 'Your request has been forwarded to the faculty member for confirmation.'
          : 'Confirm details and provide the purpose for this meeting.'
      }
    >
      {isBooked ? (
        <div className="text-center py-4 space-y-4">
          <div className="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-7 h-7" />
          </div>
          <div className="space-y-1">
            <p className="text-sm font-bold text-slate-900">
              Meeting Request Submitted (Status: REQUESTED)
            </p>
            <p className="text-xs text-slate-500">
              {faculty.full_name} · {formatDate(date)} ({formatTimeRange(slot.start_time, slot.end_time)} IST)
            </p>
          </div>
          <div className="pt-2">
            <Button onClick={handleModalClose} className="w-full">
              Done
            </Button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          {errorMessage && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-start gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span className="flex-1">{errorMessage}</span>
            </div>
          )}

          {/* Slot Summary Card */}
          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs">
            <div className="flex items-center gap-2 text-slate-700 font-semibold">
              <User className="w-4 h-4 text-brand-600 shrink-0" />
              <span>{faculty.full_name}</span>
              <span className="text-slate-400 font-normal">({faculty.title})</span>
            </div>
            <div className="flex items-center gap-2 text-slate-600">
              <Building2 className="w-4 h-4 text-slate-400 shrink-0" />
              <span>{faculty.department_name} · Office: {faculty.office_location}</span>
            </div>
            <div className="flex items-center justify-between pt-1 border-t border-slate-200/60 font-medium">
              <span className="inline-flex items-center gap-1.5 text-slate-700">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                {formatDate(date)}
              </span>
              <span className="inline-flex items-center gap-1.5 text-brand-700 font-bold bg-brand-50 px-2 py-0.5 rounded-md border border-brand-200">
                <Clock className="w-3.5 h-3.5" />
                {formatTimeRange(slot.start_time, slot.end_time)} IST
              </span>
            </div>
          </div>

          <Textarea
            label="Purpose of Meeting / Agenda"
            placeholder="E.g., Discuss capstone project thesis outline, review lab experiment findings..."
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={3}
            required
            helperText="Provide a clear, brief agenda to help faculty prepare."
          />

          <div className="flex justify-end gap-2.5 pt-2">
            <Button type="button" variant="outline" onClick={handleModalClose} disabled={mutation.isPending}>
              Cancel
            </Button>
            <Button type="submit" isLoading={mutation.isPending}>
              Confirm Request
            </Button>
          </div>
        </form>
      )}
    </Modal>
  );
};
