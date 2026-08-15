from datetime import datetime, date, time, timedelta
from typing import List, Optional
from zoneinfo import ZoneInfo
from app.core.config import settings
from app.core.time_utils import get_current_time


class TimeInterval:
    """
    Represents a half-open time interval [start_minutes, end_minutes)
    where minutes are counted from midnight (0 to 1440).
    """
    def __init__(self, start_minutes: int, end_minutes: int):
        if end_minutes <= start_minutes:
            raise ValueError(f"end_minutes ({end_minutes}) must be strictly greater than start_minutes ({start_minutes})")
        self.start_minutes = max(0, start_minutes)
        self.end_minutes = min(1440, end_minutes)

    @classmethod
    def from_time(cls, start_t: time, end_t: time) -> "TimeInterval":
        s = start_t.hour * 60 + start_t.minute
        e = end_t.hour * 60 + end_t.minute
        return cls(s, e)

    @classmethod
    def from_datetimes_on_date(cls, start_dt: datetime, end_dt: datetime, target_date: date, tz: ZoneInfo) -> Optional["TimeInterval"]:
        """
        Convert timezone-aware datetimes to a TimeInterval restricted to target_date in local timezone.
        """
        local_start = start_dt.astimezone(tz)
        local_end = end_dt.astimezone(tz)

        # Target date local boundaries
        target_start = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0, tzinfo=tz)
        target_end = target_start + timedelta(days=1)

        if local_end <= target_start or local_start >= target_end:
            return None

        # Clamp to target date boundaries
        clamped_start = max(local_start, target_start)
        clamped_end = min(local_end, target_end)

        s_min = (clamped_start - target_start).total_seconds() / 60
        e_min = (clamped_end - target_start).total_seconds() / 60

        s_int = int(round(s_min))
        e_int = int(round(e_min))

        if e_int <= s_int:
            return None

        return cls(s_int, e_int)

    def overlaps(self, other: "TimeInterval") -> bool:
        """Two intervals overlap iff max(start) < min(end). Boundary contact is NOT an overlap."""
        return max(self.start_minutes, other.start_minutes) < min(self.end_minutes, other.end_minutes)

    def subtract(self, block: "TimeInterval") -> List["TimeInterval"]:
        """Subtract a blocking interval from this interval. Returns 0, 1, or 2 remaining intervals."""
        if not self.overlaps(block):
            return [TimeInterval(self.start_minutes, self.end_minutes)]

        result = []
        # Left piece remaining
        if self.start_minutes < block.start_minutes:
            result.append(TimeInterval(self.start_minutes, block.start_minutes))

        # Right piece remaining
        if block.end_minutes < self.end_minutes:
            result.append(TimeInterval(block.end_minutes, self.end_minutes))

        return result

    @property
    def start_time_str(self) -> str:
        h = self.start_minutes // 60
        m = self.start_minutes % 60
        return f"{h:02d}:{m:02d}"

    @property
    def end_time_str(self) -> str:
        h = self.end_minutes // 60
        m = self.end_minutes % 60
        return f"{h:02d}:{m:02d}"

    def __repr__(self) -> str:
        return f"TimeInterval({self.start_time_str} - {self.end_time_str})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TimeInterval):
            return False
        return self.start_minutes == other.start_minutes and self.end_minutes == other.end_minutes


class SchedulingEngine:
    """
    Pure mathematical interval set algebra scheduling engine.
    Calculates final bookable continuous windows and discrete slots
    according to the 5-Tier Precedence Hierarchy.
    """

    @staticmethod
    def merge_intervals(intervals: List[TimeInterval]) -> List[TimeInterval]:
        """Merge overlapping or contiguous intervals into a minimal sorted list of continuous intervals."""
        if not intervals:
            return []

        sorted_intervals = sorted(intervals, key=lambda i: (i.start_minutes, i.end_minutes))
        merged = [sorted_intervals[0]]

        for current in sorted_intervals[1:]:
            last = merged[-1]
            if current.start_minutes <= last.end_minutes:
                # Overlapping or adjacent, merge
                merged[-1] = TimeInterval(last.start_minutes, max(last.end_minutes, current.end_minutes))
            else:
                merged.append(current)

        return merged

    @staticmethod
    def subtract_intervals(
        base_intervals: List[TimeInterval],
        blocked_intervals: List[TimeInterval],
    ) -> List[TimeInterval]:
        """Subtract a list of blocking intervals from a list of base availability intervals."""
        current_intervals = SchedulingEngine.merge_intervals(base_intervals)

        for block in blocked_intervals:
            next_intervals = []
            for base in current_intervals:
                next_intervals.extend(base.subtract(block))
            current_intervals = next_intervals

        return current_intervals

    @classmethod
    def compute_final_available_windows(
        cls,
        regular_intervals: List[TimeInterval],
        temporary_intervals: List[TimeInterval],
        blocked_intervals: List[TimeInterval],
        leave_intervals: List[TimeInterval],
        booked_intervals: Optional[List[TimeInterval]] = None,
    ) -> List[TimeInterval]:
        r"""
        Compute A_final = ((R \ B) U T \ B) \ (L U K) = ((R U T) \ B) \ (L U K)
        Enforces:
        1. Base availability combines Regular availability (R) and Temporary availability (T).
           Temporary availability is valid on any date, regardless of whether regular hours exist.
        2. Temporary blocks (B) subtract from all base availability windows.
        3. Approved leave (L) strictly overrides and subtracts from ALL availability (Tier 2 precedence).
        4. Existing booked appointments (K) subtract from ALL availability (Tier 1 precedence).
        """
        # Step 1 & 2: Regular minus Blocks
        r_minus_b = cls.subtract_intervals(regular_intervals, blocked_intervals)

        # Step 3: Union Temporary Availability
        combined = cls.merge_intervals(r_minus_b + temporary_intervals)

        # Step 4: Subtract Blocks again (in case temp avail overlapped a block)
        combined_minus_b = cls.subtract_intervals(combined, blocked_intervals)

        # Step 5: Subtract Leave (Leave strictly overrides regular & temp avail)
        after_leave = cls.subtract_intervals(combined_minus_b, leave_intervals)

        # Step 6: Subtract Booked appointments (Phase 4 compatibility)
        if booked_intervals:
            final_windows = cls.subtract_intervals(after_leave, booked_intervals)
        else:
            final_windows = after_leave

        return final_windows

    @classmethod
    def generate_discrete_slots(
        cls,
        available_windows: List[TimeInterval],
        target_date: date,
        duration_minutes: int = 30,
        min_lead_notice_minutes: int = 0,
        current_time: Optional[datetime] = None,
        tz_name: str = "Asia/Kolkata",
    ) -> List[dict]:
        """
        Slice continuous available windows into discrete slots of duration_minutes.
        Filters out past slots on current_date based on current_time + min_lead_notice_minutes.
        """
        tz = ZoneInfo(tz_name)
        now = current_time if current_time is not None else get_current_time(tz_name)
        if now.tzinfo is None:
            now = now.replace(tzinfo=tz)
        else:
            now = now.astimezone(tz)

        # Determine cutoff timestamp in local time
        earliest_booking_time = now + timedelta(minutes=min_lead_notice_minutes)

        slots = []
        for window in available_windows:
            slot_start = window.start_minutes
            while slot_start + duration_minutes <= window.end_minutes:
                slot_end = slot_start + duration_minutes

                slot_start_time = time(hour=slot_start // 60, minute=slot_start % 60)
                slot_end_time = time(hour=slot_end // 60, minute=slot_end % 60)

                slot_start_dt = datetime.combine(target_date, slot_start_time, tzinfo=tz)
                slot_end_dt = datetime.combine(target_date, slot_end_time, tzinfo=tz)

                # Filter out past slots (only applies if target_date <= now.date())
                if target_date < now.date():
                    # Strictly past date, no slots allowed
                    pass
                elif target_date == now.date():
                    # Today, filter past slots
                    if slot_start_dt >= earliest_booking_time:
                        slots.append({
                            "start_datetime": slot_start_dt,
                            "end_datetime": slot_end_dt,
                            "start_time": f"{slot_start_time.hour:02d}:{slot_start_time.minute:02d}",
                            "end_time": f"{slot_end_time.hour:02d}:{slot_end_time.minute:02d}",
                            "duration_minutes": duration_minutes,
                            "status": "AVAILABLE",
                        })
                else:
                    # Future date, all generated slots are valid
                    slots.append({
                        "start_datetime": slot_start_dt,
                        "end_datetime": slot_end_dt,
                        "start_time": f"{slot_start_time.hour:02d}:{slot_start_time.minute:02d}",
                        "end_time": f"{slot_end_time.hour:02d}:{slot_end_time.minute:02d}",
                        "duration_minutes": duration_minutes,
                        "status": "AVAILABLE",
                    })

                slot_start += duration_minutes

        return slots
