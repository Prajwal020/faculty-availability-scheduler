import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { availabilityApi, TemporaryAvailabilityCreatePayload } from '../../api/availability';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { Input } from '../../components/ui/Input';
import { EmptyState } from '../../components/ui/EmptyState';
import { CardSkeleton } from '../../components/ui/Skeleton';
import { formatDate, formatTimeRange, getTodayDateString } from '../../utils/formatters';
import {
  Sparkles,
  Plus,
  Trash2,
  Calendar,
  Clock,
  AlertCircle,
} from 'lucide-react';

export const FacultyTemporaryAvailability: React.FC = () => {
  const queryClient = useQueryClient();
  const today = getTodayDateString();
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [date, setDate] = useState(today);
  const [startTime, setStartTime] = useState('14:00');
  const [endTime, setEndTime] = useState('16:00');
  const [reason, setReason] = useState('');
  const [formError, setFormError] = useState<string | null>(null);

  const { data: temporaryWindows = [], isLoading } = useQuery({
    queryKey: ['my-temporary-availability'],
    queryFn: () => availabilityApi.listTemporary(),
  });

  const createMutation = useMutation({
    mutationFn: (payload: TemporaryAvailabilityCreatePayload) =>
      availabilityApi.createTemporary(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-temporary-availability'] });
      setIsAddModalOpen(false);
      setReason('');
      setFormError(null);
    },
    onError: (err: any) => {
      setFormError(err.message || 'Failed to create pop-up availability window.');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => availabilityApi.deleteTemporary(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-temporary-availability'] });
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (startTime >= endTime) {
      setFormError('End time must be strictly after start time.');
      return;
    }

    setFormError(null);
    createMutation.mutate({
      date,
      start_time: `${startTime}:00`,
      end_time: `${endTime}:00`,
      reason: reason ? reason.trim() : undefined,
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Pop-up Extra Office Hours
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Add one-time extra availability slots for a specific calendar date (e.g. before exams or after cancelled lectures).
          </p>
        </div>

        <Button
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => {
            setIsAddModalOpen(true);
            setFormError(null);
          }}
        >
          Add Pop-up Hours
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-5 space-y-3">
              <CardSkeleton />
              <CardSkeleton />
            </div>
          ) : temporaryWindows.length === 0 ? (
            <div className="p-8">
              <EmptyState
                icon={<Sparkles className="w-8 h-8 text-brand-500" />}
                title="No Pop-up Hours Active"
                description="You haven't scheduled any one-time extra availability windows."
                actionLabel="Add Pop-up Hours"
                onAction={() => setIsAddModalOpen(true)}
              />
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {temporaryWindows.map((win) => (
                <div
                  key={win.id}
                  className="p-5 hover:bg-slate-50/70 transition flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-brand-600" />
                      <span className="text-sm font-bold text-slate-900">
                        {formatDate(win.date)}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-xs font-semibold text-brand-700 bg-brand-50 px-2.5 py-1 rounded-md border border-brand-200 w-fit">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{formatTimeRange(win.start_time, win.end_time)} IST</span>
                    </div>

                    {win.reason && (
                      <p className="text-xs text-slate-600 italic">"{win.reason}"</p>
                    )}
                  </div>

                  <Button
                    variant="danger"
                    size="sm"
                    leftIcon={<Trash2 className="w-3.5 h-3.5" />}
                    onClick={() => deleteMutation.mutate(win.id)}
                    isLoading={deleteMutation.isPending}
                  >
                    Remove
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Add Pop-up Office Hours"
        description="Schedule a temporary one-time availability window on a specific date."
      >
        <form onSubmit={handleCreate} className="space-y-4">
          {formError && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{formError}</span>
            </div>
          )}

          <Input
            label="Date"
            type="date"
            min={today}
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
          />

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Start Time (IST)"
              type="time"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              required
            />
            <Input
              label="End Time (IST)"
              type="time"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              required
            />
          </div>

          <Input
            label="Reason / Note (optional)"
            placeholder="E.g., Extra office hours before midterm exam"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />

          <div className="flex justify-end gap-2.5 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsAddModalOpen(false)}
              disabled={createMutation.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" isLoading={createMutation.isPending}>
              Save Pop-up Hours
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
