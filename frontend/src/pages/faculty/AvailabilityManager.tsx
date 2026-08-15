import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { availabilityApi, RegularAvailabilityCreatePayload } from '../../api/availability';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { Select, Input } from '../../components/ui/Input';
import { getDayName, formatTimeRange } from '../../utils/formatters';
import {
  Plus,
  Trash2,
  AlertCircle,
} from 'lucide-react';

export const FacultyAvailabilityManager: React.FC = () => {
  const queryClient = useQueryClient();
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [dayOfWeek, setDayOfWeek] = useState<number>(0);
  const [startTime, setStartTime] = useState('09:00');
  const [endTime, setEndTime] = useState('12:00');
  const [slotDuration, setSlotDuration] = useState<number>(30);
  const [formError, setFormError] = useState<string | null>(null);

  const { data: recurringHours = [] } = useQuery({
    queryKey: ['my-regular-availability'],
    queryFn: () => availabilityApi.listRegular(),
  });

  const createMutation = useMutation({
    mutationFn: (payload: RegularAvailabilityCreatePayload) =>
      availabilityApi.createRegular(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-regular-availability'] });
      setIsAddModalOpen(false);
      setFormError(null);
    },
    onError: (err: any) => {
      setFormError(err.message || 'Failed to create availability window.');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => availabilityApi.deleteRegular(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-regular-availability'] });
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
      day_of_week: Number(dayOfWeek),
      start_time: `${startTime}:00`,
      end_time: `${endTime}:00`,
      slot_duration_minutes: Number(slotDuration),
      is_active: true,
    });
  };

  const days = [0, 1, 2, 3, 4, 5, 6];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Weekly Recurring Office Hours
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Define your regular weekly availability schedule for student appointments.
          </p>
        </div>

        <Button
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => {
            setIsAddModalOpen(true);
            setFormError(null);
          }}
        >
          Add Recurring Window
        </Button>
      </div>

      {/* Days Table */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {days.map((dayNum) => {
          const windowsForDay = recurringHours.filter((h) => h.day_of_week === dayNum);
          const isWeekend = dayNum === 5 || dayNum === 6;

          return (
            <Card key={dayNum} className={isWeekend ? 'bg-slate-50/50' : 'bg-white'}>
              <CardHeader className="p-4 pb-2 flex flex-row items-center justify-between">
                <CardTitle className="text-xs font-bold uppercase tracking-wider text-slate-700">
                  {getDayName(dayNum)}
                </CardTitle>
                <span className="text-[11px] font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded-md">
                  {windowsForDay.length} window(s)
                </span>
              </CardHeader>

              <CardContent className="p-4 pt-2 space-y-2">
                {windowsForDay.length === 0 ? (
                  <p className="text-xs text-slate-600 italic py-2">No recurring hours</p>
                ) : (
                  windowsForDay.map((win) => (
                    <div
                      key={win.id}
                      className="p-3 bg-brand-50/60 rounded-xl border border-brand-200/70 flex items-center justify-between gap-2"
                    >
                      <div className="space-y-0.5">
                        <p className="text-xs font-bold text-brand-900">
                          {formatTimeRange(win.start_time, win.end_time)}
                        </p>
                        <p className="text-[10px] text-brand-700 font-semibold">
                          {win.slot_duration_minutes} min slots
                        </p>
                      </div>

                      <button
                        onClick={() => deleteMutation.mutate(win.id)}
                        disabled={deleteMutation.isPending}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-white transition"
                        title="Delete window"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Add Recurring Window Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Add Weekly Recurring Window"
        description="Add a recurring window of office hours that repeats every week on the chosen day."
      >
        <form onSubmit={handleCreate} className="space-y-4">
          {formError && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{formError}</span>
            </div>
          )}

          <Select
            label="Day of Week"
            value={dayOfWeek}
            onChange={(e) => setDayOfWeek(Number(e.target.value))}
            options={[
              { value: 0, label: 'Monday' },
              { value: 1, label: 'Tuesday' },
              { value: 2, label: 'Wednesday' },
              { value: 3, label: 'Thursday' },
              { value: 4, label: 'Friday' },
              { value: 5, label: 'Saturday' },
              { value: 6, label: 'Sunday' },
            ]}
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

          <Select
            label="Slot Duration (Minutes)"
            value={slotDuration}
            onChange={(e) => setSlotDuration(Number(e.target.value))}
            options={[
              { value: 15, label: '15 Minutes' },
              { value: 30, label: '30 Minutes (Standard)' },
              { value: 45, label: '45 Minutes' },
              { value: 60, label: '60 Minutes' },
            ]}
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
              Save Window
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
