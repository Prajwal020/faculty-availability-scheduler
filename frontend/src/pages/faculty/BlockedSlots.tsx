import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { availabilityApi, BlockedSlotCreatePayload } from '../../api/availability';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { Input, Textarea } from '../../components/ui/Input';
import { EmptyState } from '../../components/ui/EmptyState';
import { CardSkeleton } from '../../components/ui/Skeleton';
import { getTodayDateString } from '../../utils/formatters';
import {
  Ban,
  Plus,
  Trash2,
  AlertCircle,
} from 'lucide-react';

export const FacultyBlockedSlots: React.FC = () => {
  const queryClient = useQueryClient();
  const today = getTodayDateString();
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [startDate, setStartDate] = useState(today);
  const [startTime, setStartTime] = useState('10:00');
  const [endDate, setEndDate] = useState(today);
  const [endTime, setEndTime] = useState('11:30');
  const [reason, setReason] = useState('');
  const [formError, setFormError] = useState<string | null>(null);

  const { data: blockedSlots = [], isLoading } = useQuery({
    queryKey: ['my-blocked-slots'],
    queryFn: () => availabilityApi.listBlocked(),
  });

  const createMutation = useMutation({
    mutationFn: (payload: BlockedSlotCreatePayload) => availabilityApi.createBlocked(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-blocked-slots'] });
      setIsAddModalOpen(false);
      setReason('');
      setFormError(null);
    },
    onError: (err: any) => {
      setFormError(err.message || 'Failed to block time slot.');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => availabilityApi.deleteBlocked(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-blocked-slots'] });
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    const startIso = `${startDate}T${startTime}:00`;
    const endIso = `${endDate}T${endTime}:00`;

    if (new Date(startIso) >= new Date(endIso)) {
      setFormError('End date/time must be strictly after start date/time.');
      return;
    }
    if (!reason.trim()) {
      setFormError('Reason for blocking is required.');
      return;
    }

    setFormError(null);
    createMutation.mutate({
      start_datetime: startIso,
      end_datetime: endIso,
      reason: reason.trim(),
    });
  };

  const formatDateTimeDisplay = (isoStr: string) => {
    try {
      const d = new Date(isoStr);
      return d.toLocaleString('en-IN', {
        dateStyle: 'medium',
        timeStyle: 'short',
        timeZone: 'Asia/Kolkata',
      });
    } catch {
      return isoStr;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Blocked Periods</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Carve out temporary busy times (e.g. department meetings, thesis defenses) to block appointment bookings.
          </p>
        </div>

        <Button
          variant="danger"
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => {
            setIsAddModalOpen(true);
            setFormError(null);
          }}
        >
          Block New Period
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-5 space-y-3">
              <CardSkeleton />
              <CardSkeleton />
            </div>
          ) : blockedSlots.length === 0 ? (
            <div className="p-8">
              <EmptyState
                icon={<Ban className="w-8 h-8 text-red-500" />}
                title="No Blocked Periods"
                description="You currently have no temporary blocked windows configured."
                actionLabel="Block a Period"
                onAction={() => setIsAddModalOpen(true)}
              />
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {blockedSlots.map((block) => (
                <div
                  key={block.id}
                  className="p-5 hover:bg-slate-50/70 transition flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2 text-xs font-bold text-red-700 bg-red-50 px-2.5 py-1 rounded-md border border-red-200 w-fit">
                      <Ban className="w-3.5 h-3.5" />
                      <span>
                        {formatDateTimeDisplay(block.start_datetime)} –{' '}
                        {formatDateTimeDisplay(block.end_datetime)}
                      </span>
                    </div>

                    <p className="text-xs text-slate-800 font-semibold">
                      Reason: <span className="font-normal text-slate-600">{block.reason}</span>
                    </p>
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    leftIcon={<Trash2 className="w-3.5 h-3.5 text-red-500" />}
                    onClick={() => deleteMutation.mutate(block.id)}
                    isLoading={deleteMutation.isPending}
                  >
                    Unblock
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Block Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Block Time Period"
        description="Select a timeframe during which you are unavailable for student appointments."
      >
        <form onSubmit={handleCreate} className="space-y-4">
          {formError && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{formError}</span>
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Start Date"
              type="date"
              min={today}
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              required
            />
            <Input
              label="Start Time (IST)"
              type="time"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="End Date"
              type="date"
              min={startDate}
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
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

          <Textarea
            label="Reason for Blocking"
            placeholder="E.g., Department Faculty Council Meeting"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={2}
            required
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
            <Button type="submit" variant="danger" isLoading={createMutation.isPending}>
              Block Period
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
