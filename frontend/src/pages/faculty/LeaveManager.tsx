import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { leaveApi, LeaveCreatePayload } from '../../api/leave';
import { LeaveType } from '../../types';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import { Input, Select, Textarea } from '../../components/ui/Input';
import { EmptyState } from '../../components/ui/EmptyState';
import { CardSkeleton } from '../../components/ui/Skeleton';
import { formatDate, getTodayDateString } from '../../utils/formatters';
import {
  CalendarOff,
  Plus,
  Trash2,
  Calendar,
  AlertCircle,
} from 'lucide-react';

export const FacultyLeaveManager: React.FC = () => {
  const queryClient = useQueryClient();
  const today = getTodayDateString();
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [startDate, setStartDate] = useState(today);
  const [endDate, setEndDate] = useState(today);
  const [leaveType, setLeaveType] = useState<LeaveType>('FULL_DAY');
  const [reason, setReason] = useState('');
  const [formError, setFormError] = useState<string | null>(null);

  const { data: leaves = [], isLoading } = useQuery({
    queryKey: ['my-leaves'],
    queryFn: () => leaveApi.listLeaves(),
  });

  const createMutation = useMutation({
    mutationFn: (payload: LeaveCreatePayload) => leaveApi.createLeave(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-leaves'] });
      setIsAddModalOpen(false);
      setReason('');
      setFormError(null);
    },
    onError: (err: any) => {
      setFormError(err.message || 'Failed to submit leave declaration.');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => leaveApi.deleteLeave(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-leaves'] });
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (startDate > endDate) {
      setFormError('End date must be on or after start date.');
      return;
    }
    if (!reason.trim()) {
      setFormError('Reason for leave is required.');
      return;
    }

    setFormError(null);
    createMutation.mutate({
      start_date: startDate,
      end_date: endDate,
      leave_type: leaveType,
      reason: reason.trim(),
    });
  };

  const getLeaveTypeBadge = (type: LeaveType) => {
    switch (type) {
      case 'FULL_DAY':
        return <span className="text-[11px] font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded">Full Day</span>;
      case 'HALF_DAY_MORNING':
        return <span className="text-[11px] font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded">Morning (Before 13:00)</span>;
      case 'HALF_DAY_AFTERNOON':
        return <span className="text-[11px] font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded">Afternoon (After 13:00)</span>;
      case 'MULTI_DAY':
        return <span className="text-[11px] font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded">Multi-Day</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Leave Declarations
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Declare scheduled leaves or duty absences. Leave suppresses all regular availability on affected dates.
          </p>
        </div>

        <Button
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => {
            setIsAddModalOpen(true);
            setFormError(null);
          }}
        >
          Declare Leave
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-5 space-y-3">
              <CardSkeleton />
              <CardSkeleton />
            </div>
          ) : leaves.length === 0 ? (
            <div className="p-8">
              <EmptyState
                icon={<CalendarOff className="w-8 h-8 text-amber-500" />}
                title="No Leave Records"
                description="You currently have no scheduled leaves or absence declarations."
                actionLabel="Declare Leave"
                onAction={() => setIsAddModalOpen(true)}
              />
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {leaves.map((leave) => (
                <div
                  key={leave.id}
                  className="p-5 hover:bg-slate-50/70 transition flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1.5">
                    <div className="flex flex-wrap items-center gap-2.5">
                      <Calendar className="w-4 h-4 text-brand-600" />
                      <span className="text-sm font-bold text-slate-900">
                        {formatDate(leave.start_date)}
                        {leave.start_date !== leave.end_date && ` – ${formatDate(leave.end_date)}`}
                      </span>
                      {getLeaveTypeBadge(leave.leave_type)}
                      <Badge size="sm" status={leave.status} />
                    </div>

                    <p className="text-xs text-slate-700 font-medium">
                      Reason: <span className="text-slate-600 font-normal">{leave.reason}</span>
                    </p>
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    leftIcon={<Trash2 className="w-3.5 h-3.5 text-red-500" />}
                    onClick={() => deleteMutation.mutate(leave.id)}
                    isLoading={deleteMutation.isPending}
                  >
                    Cancel Leave
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Leave Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Declare Faculty Leave"
        description="Submit a planned absence. Availability slots during this period will automatically be removed for students."
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
              onChange={(e) => {
                setStartDate(e.target.value);
                if (e.target.value > endDate) setEndDate(e.target.value);
              }}
              required
            />
            <Input
              label="End Date"
              type="date"
              min={startDate}
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              required
            />
          </div>

          <Select
            label="Leave Type"
            value={leaveType}
            onChange={(e) => setLeaveType(e.target.value as LeaveType)}
            options={[
              { value: 'FULL_DAY', label: 'Full Day (All Day Absence)' },
              { value: 'HALF_DAY_MORNING', label: 'Half Day — Morning (Before 13:00)' },
              { value: 'HALF_DAY_AFTERNOON', label: 'Half Day — Afternoon (After 13:00)' },
              { value: 'MULTI_DAY', label: 'Multi-Day Period' },
            ]}
          />

          <Textarea
            label="Reason for Leave"
            placeholder="E.g., International Academic Conference on Distributed Computing"
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
            <Button type="submit" isLoading={createMutation.isPending}>
              Submit Leave
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
