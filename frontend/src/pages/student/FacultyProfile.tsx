import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { facultyApi } from '../../api/faculty';
import { availabilityApi } from '../../api/availability';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { EmptyState } from '../../components/ui/EmptyState';
import { CardSkeleton } from '../../components/ui/Skeleton';
import { BookingModal } from '../../components/appointments/BookingModal';
import { BookableSlot } from '../../types';
import {
  getTodayDateString,
  addDays,
  formatDate,
  formatTimeRange,
  getDayName,
} from '../../utils/formatters';
import {
  ArrowLeft,
  Building2,
  MapPin,
  Calendar,
  Clock,
  CalendarOff,
  Mail,
  Sparkles,
} from 'lucide-react';

export const FacultyProfile: React.FC = () => {
  const { facultyId } = useParams<{ facultyId: string }>();
  const today = getTodayDateString();
  const [selectedDate, setSelectedDate] = useState<string>(today);
  const [selectedSlot, setSelectedSlot] = useState<BookableSlot | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Fetch Faculty Profile
  const { data: faculty, isLoading: isFacultyLoading } = useQuery({
    queryKey: ['faculty-profile', facultyId],
    queryFn: () => facultyApi.getFacultyPublicProfile(facultyId!),
    enabled: !!facultyId,
  });

  // Fetch Real-time Availability for the selected date
  const { data: availability, isLoading: isAvailLoading, refetch } = useQuery({
    queryKey: ['faculty-availability', facultyId, selectedDate],
    queryFn: () => availabilityApi.getFacultyAvailability(facultyId!, selectedDate, 30),
    enabled: !!facultyId && !!selectedDate,
  });

  if (isFacultyLoading) {
    return (
      <div className="space-y-4">
        <CardSkeleton />
        <CardSkeleton />
      </div>
    );
  }

  if (!faculty) {
    return (
      <EmptyState
        title="Faculty Member Not Found"
        description="The requested faculty member profile could not be located."
        actionLabel="Back to Directory"
        onAction={() => window.location.assign('/student/faculty')}
      />
    );
  }

  const handleSlotClick = (slot: BookableSlot) => {
    setSelectedSlot(slot);
    setIsModalOpen(true);
  };

  // Generate 7 upcoming date quick-selector chips
  const dateChips = Array.from({ length: 7 }, (_, i) => {
    const dStr = addDays(today, i);
    const [y, m, d] = dStr.split('-').map(Number);
    const dateObj = new Date(y, m - 1, d);
    const dayOfWeek = (dateObj.getDay() + 6) % 7; // 0=Mon, 6=Sun
    return {
      date: dStr,
      dayName: getDayName(dayOfWeek, true),
      dayNum: d,
      isToday: i === 0,
    };
  });

  return (
    <div className="space-y-6">
      {/* Back button */}
      <Link
        to="/student/faculty"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Faculty Directory
      </Link>

      {/* Faculty Profile Card */}
      <Card className="border-t-4 border-t-brand-600 shadow-sm">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="flex items-start gap-4">
              <div className="w-16 h-16 rounded-2xl bg-brand-100 border border-brand-200 text-brand-700 font-bold text-2xl flex items-center justify-center shrink-0 shadow-2xs">
                {faculty.full_name.charAt(0)}
              </div>
              <div className="space-y-1.5">
                <div className="flex flex-wrap items-center gap-2">
                  <h1 className="text-xl font-bold text-slate-900">{faculty.full_name}</h1>
                  <Badge status={faculty.meeting_mode} />
                </div>
                <p className="text-xs font-semibold text-brand-700">{faculty.title}</p>
                <div className="flex flex-wrap items-center gap-4 text-xs text-slate-600 pt-1">
                  <span className="flex items-center gap-1.5">
                    <Building2 className="w-3.5 h-3.5 text-slate-400" />
                    {faculty.department_name} ({faculty.department_code})
                  </span>
                  <span className="flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    Office: {faculty.office_location}
                  </span>
                  <span className="flex items-center gap-1.5">
                    <Mail className="w-3.5 h-3.5 text-slate-400" />
                    {faculty.email}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {faculty.bio && (
            <div className="mt-4 pt-4 border-t border-slate-100 text-xs text-slate-600 leading-relaxed">
              <span className="font-semibold text-slate-900">About: </span>
              {faculty.bio}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Availability & Booking Section */}
      <Card>
        <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-brand-600" />
              Available Appointment Slots
            </CardTitle>
            <p className="text-xs text-slate-500 mt-0.5">
              Select a date to view real-time calculated 30-minute office hour slots
            </p>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="date"
              min={today}
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="text-xs px-3 py-1.5 rounded-lg border border-slate-300 bg-white font-medium text-slate-700 focus:ring-2 focus:ring-brand-500"
            />
          </div>
        </CardHeader>

        <CardContent className="p-6 space-y-6">
          {/* Quick Date Select Chips */}
          <div className="grid grid-cols-7 gap-2 overflow-x-auto pb-1">
            {dateChips.map((chip) => {
              const isSelected = selectedDate === chip.date;
              return (
                <button
                  key={chip.date}
                  onClick={() => setSelectedDate(chip.date)}
                  className={`p-3 rounded-xl border text-center transition flex flex-col items-center gap-1 ${
                    isSelected
                      ? 'bg-brand-600 text-white border-brand-600 shadow-sm'
                      : 'bg-white text-slate-700 border-slate-200 hover:border-brand-400 hover:bg-brand-50/30'
                  }`}
                >
                  <span className={`text-[10px] font-bold uppercase ${isSelected ? 'text-brand-100' : 'text-slate-600'}`}>
                    {chip.dayName}
                  </span>
                  <span className="text-base font-bold">{chip.dayNum}</span>
                  {chip.isToday && (
                    <span
                      className={`text-[9px] font-bold px-1 rounded ${
                        isSelected ? 'bg-brand-700 text-white' : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      Today
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          {/* Selected Date Header */}
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-slate-400" />
              <span className="text-xs font-bold text-slate-900">
                Slots for {formatDate(selectedDate)}
              </span>
            </div>
            <span className="text-xs text-slate-600">Asia/Kolkata (IST)</span>
          </div>

          {/* Availability Status & Slots Grid */}
          {isAvailLoading ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              <div className="h-14 bg-slate-100 rounded-xl animate-pulse" />
              <div className="h-14 bg-slate-100 rounded-xl animate-pulse" />
              <div className="h-14 bg-slate-100 rounded-xl animate-pulse" />
              <div className="h-14 bg-slate-100 rounded-xl animate-pulse" />
            </div>
          ) : availability?.is_on_leave ? (
            <div className="p-6 bg-amber-50 rounded-2xl border border-amber-200 text-center space-y-2">
              <div className="w-10 h-10 bg-amber-100 text-amber-700 rounded-full flex items-center justify-center mx-auto">
                <CalendarOff className="w-5 h-5" />
              </div>
              <h4 className="text-xs font-bold text-amber-900">Faculty On Approved Leave</h4>
              <p className="text-xs text-amber-700 max-w-sm mx-auto">
                {faculty.full_name} is unavailable for appointments on this date due to approved leave. Please select another date.
              </p>
            </div>
          ) : availability?.slots && availability.slots.length > 0 ? (
            <div className="space-y-3">
              <p className="text-xs text-slate-500">
                Found <strong>{availability.total_slots}</strong> available slot(s). Click an available time to request a meeting:
              </p>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                {availability.slots.map((slot, idx) => (
                  <button
                    key={`${slot.start_time}-${idx}`}
                    onClick={() => handleSlotClick(slot)}
                    className="p-3.5 rounded-xl border border-emerald-200 bg-emerald-50/60 hover:bg-emerald-100/80 hover:border-emerald-400 text-emerald-900 transition-all flex flex-col items-center justify-center gap-1 group shadow-2xs hover:shadow-xs active:scale-[0.98]"
                  >
                    <span className="text-xs font-bold tracking-tight">
                      {formatTimeRange(slot.start_time, slot.end_time)}
                    </span>
                    <span className="text-[10px] font-semibold text-emerald-700 group-hover:text-emerald-800 flex items-center gap-1">
                      <Sparkles className="w-3 h-3" /> Request Slot
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <EmptyState
              icon={<Clock className="w-6 h-6 text-slate-400" />}
              title="No Available Slots on this Date"
              description={`No free appointment windows are available for ${formatDate(
                selectedDate
              )}. The faculty member may not have scheduled hours or existing appointments may fill the schedule.`}
            />
          )}
        </CardContent>
      </Card>

      {/* Booking Modal */}
      {selectedSlot && (
        <BookingModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          faculty={faculty}
          date={selectedDate}
          slot={selectedSlot}
          onSuccess={() => refetch()}
        />
      )}
    </div>
  );
};
