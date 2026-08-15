from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo
import pytest

from app.services.scheduling_engine import TimeInterval, SchedulingEngine


def test_time_interval_creation_and_validation():
    # Valid interval 09:00 to 12:00 (540 to 720 minutes)
    iv = TimeInterval(540, 720)
    assert iv.start_minutes == 540
    assert iv.end_minutes == 720
    assert iv.start_time_str == "09:00"
    assert iv.end_time_str == "12:00"

    # Invalid interval where end <= start
    with pytest.raises(ValueError):
        TimeInterval(720, 540)
    with pytest.raises(ValueError):
        TimeInterval(600, 600)


def test_time_interval_overlaps():
    iv1 = TimeInterval(540, 720)  # 09:00 - 12:00
    iv2 = TimeInterval(600, 660)  # 10:00 - 11:00 (inside)
    iv3 = TimeInterval(720, 780)  # 12:00 - 13:00 (adjacent at boundary)
    iv4 = TimeInterval(480, 540)  # 08:00 - 09:00 (adjacent at boundary)
    iv5 = TimeInterval(800, 900)  # 13:20 - 15:00 (disjoint)

    assert iv1.overlaps(iv2) is True
    assert iv1.overlaps(iv3) is False  # Boundary contact is NOT overlap
    assert iv1.overlaps(iv4) is False  # Boundary contact is NOT overlap
    assert iv1.overlaps(iv5) is False


def test_time_interval_exact_match_conflict():
    iv1 = TimeInterval(600, 660)  # 10:00 - 11:00
    iv2 = TimeInterval(600, 660)  # 10:00 - 11:00
    assert iv1.overlaps(iv2) is True


def test_time_interval_inside_and_enclosing_conflict():
    outer = TimeInterval(600, 720)  # 10:00 - 12:00
    inner = TimeInterval(630, 660)  # 10:30 - 11:00
    assert outer.overlaps(inner) is True
    assert inner.overlaps(outer) is True


def test_time_interval_partial_overlap_start_and_end():
    iv1 = TimeInterval(600, 660)  # 10:00 - 11:00
    start_overlap = TimeInterval(570, 630)  # 09:30 - 10:30
    end_overlap = TimeInterval(630, 690)    # 10:30 - 11:30

    assert iv1.overlaps(start_overlap) is True
    assert iv1.overlaps(end_overlap) is True


def test_time_interval_adjacent_no_conflict():
    iv1 = TimeInterval(600, 660)  # 10:00 - 11:00
    iv2 = TimeInterval(660, 720)  # 11:00 - 12:00
    assert iv1.overlaps(iv2) is False


def test_time_interval_subtraction_cases():
    base = TimeInterval(540, 720)  # 09:00 - 12:00

    # Case 1: Disjoint block (no overlap)
    no_overlap_block = TimeInterval(800, 900)
    res1 = base.subtract(no_overlap_block)
    assert len(res1) == 1
    assert res1[0] == TimeInterval(540, 720)

    # Case 2: Complete cover
    cover_block = TimeInterval(500, 800)
    res2 = base.subtract(cover_block)
    assert len(res2) == 0

    # Case 3: Middle split (10:00 - 11:00)
    middle_block = TimeInterval(600, 660)
    res3 = base.subtract(middle_block)
    assert len(res3) == 2
    assert res3[0] == TimeInterval(540, 600)  # 09:00 - 10:00
    assert res3[1] == TimeInterval(660, 720)  # 11:00 - 12:00

    # Case 4: Left chop (08:30 - 10:00)
    left_block = TimeInterval(510, 600)
    res4 = base.subtract(left_block)
    assert len(res4) == 1
    assert res4[0] == TimeInterval(600, 720)  # 10:00 - 12:00

    # Case 5: Right chop (11:00 - 12:30)
    right_block = TimeInterval(660, 750)
    res5 = base.subtract(right_block)
    assert len(res5) == 1
    assert res5[0] == TimeInterval(540, 660)  # 09:00 - 11:00


def test_merge_intervals():
    intervals = [
        TimeInterval(540, 600),  # 09:00 - 10:00
        TimeInterval(600, 660),  # 10:00 - 11:00 (adjacent)
        TimeInterval(720, 780),  # 12:00 - 13:00 (disjoint)
    ]
    merged = SchedulingEngine.merge_intervals(intervals)
    assert len(merged) == 2
    assert merged[0] == TimeInterval(540, 660)  # 09:00 - 11:00
    assert merged[1] == TimeInterval(720, 780)  # 12:00 - 13:00


def test_precedence_scenario_regular_only():
    regular = [TimeInterval(540, 720)]  # 09:00 - 12:00
    windows = SchedulingEngine.compute_final_available_windows(
        regular_intervals=regular,
        temporary_intervals=[],
        blocked_intervals=[],
        leave_intervals=[],
    )
    assert len(windows) == 1
    assert windows[0] == TimeInterval(540, 720)


def test_precedence_scenario_regular_with_block():
    regular = [TimeInterval(540, 720)]  # 09:00 - 12:00
    blocked = [TimeInterval(600, 630)]  # 10:00 - 10:30
    windows = SchedulingEngine.compute_final_available_windows(
        regular_intervals=regular,
        temporary_intervals=[],
        blocked_intervals=blocked,
        leave_intervals=[],
    )
    assert len(windows) == 2
    assert windows[0] == TimeInterval(540, 600)  # 09:00 - 10:00
    assert windows[1] == TimeInterval(630, 720)  # 10:30 - 12:00


def test_precedence_scenario_full_day_leave():
    regular = [TimeInterval(540, 720)]  # 09:00 - 12:00
    leave = [TimeInterval(0, 1440)]     # Full-day leave
    windows = SchedulingEngine.compute_final_available_windows(
        regular_intervals=regular,
        temporary_intervals=[],
        blocked_intervals=[],
        leave_intervals=leave,
    )
    assert len(windows) == 0


def test_precedence_scenario_leave_strictly_overrides_temp_availability():
    leave = [TimeInterval(0, 1440)]
    temp_avail = [TimeInterval(660, 690)]  # 11:00 - 11:30
    windows = SchedulingEngine.compute_final_available_windows(
        regular_intervals=[],
        temporary_intervals=temp_avail,
        blocked_intervals=[],
        leave_intervals=leave,
    )
    assert len(windows) == 0  # Leave strictly wins!


def test_precedence_scenario_temp_avail_without_regular_hours():
    # Day with no regular availability, but pop-up temporary availability 14:00 - 14:30 (840 to 870)
    temp_avail = [TimeInterval(840, 870)]
    windows = SchedulingEngine.compute_final_available_windows(
        regular_intervals=[],
        temporary_intervals=temp_avail,
        blocked_intervals=[],
        leave_intervals=[],
    )
    assert len(windows) == 1
    assert windows[0] == TimeInterval(840, 870)


def test_precedence_scenario_half_day_morning_leave():
    # Regular 09:00 - 17:00 (540 to 1020). Morning leave: 00:00 - 13:00 (0 to 780)
    regular = [TimeInterval(540, 1020)]
    morning_leave = [TimeInterval(0, 780)]
    windows = SchedulingEngine.compute_final_available_windows(
        regular_intervals=regular,
        temporary_intervals=[],
        blocked_intervals=[],
        leave_intervals=morning_leave,
    )
    assert len(windows) == 1
    assert windows[0] == TimeInterval(780, 1020)  # 13:00 - 17:00


def test_precedence_scenario_half_day_afternoon_leave():
    # Regular 09:00 - 17:00 (540 to 1020). Afternoon leave: 13:00 - 24:00 (780 to 1440)
    regular = [TimeInterval(540, 1020)]
    afternoon_leave = [TimeInterval(780, 1440)]
    windows = SchedulingEngine.compute_final_available_windows(
        regular_intervals=regular,
        temporary_intervals=[],
        blocked_intervals=[],
        leave_intervals=afternoon_leave,
    )
    assert len(windows) == 1
    assert windows[0] == TimeInterval(540, 780)  # 09:00 - 13:00


def test_slot_generation_exact_fit():
    windows = [TimeInterval(540, 660)]  # 09:00 - 11:00
    target_date = date(2026, 8, 17)
    tz = "Asia/Kolkata"
    current_time = datetime(2026, 8, 1, 8, 0, tzinfo=ZoneInfo(tz))

    slots = SchedulingEngine.generate_discrete_slots(
        available_windows=windows,
        target_date=target_date,
        duration_minutes=30,
        current_time=current_time,
        tz_name=tz,
    )

    assert len(slots) == 4
    assert slots[0]["start_time"] == "09:00"
    assert slots[0]["end_time"] == "09:30"
    assert slots[3]["start_time"] == "10:30"
    assert slots[3]["end_time"] == "11:00"


def test_slot_generation_partial_remainder():
    windows = [TimeInterval(540, 620)]  # 09:00 - 10:20 (80 min)
    target_date = date(2026, 8, 17)
    tz = "Asia/Kolkata"
    current_time = datetime(2026, 8, 1, 8, 0, tzinfo=ZoneInfo(tz))

    slots = SchedulingEngine.generate_discrete_slots(
        available_windows=windows,
        target_date=target_date,
        duration_minutes=30,
        current_time=current_time,
        tz_name=tz,
    )
    # 2 slots of 30 min (09:00-09:30, 09:30-10:00). 20 min remainder discarded.
    assert len(slots) == 2


def test_slot_generation_no_fit_window():
    # Window 09:00 - 09:29 (29 min), Duration 30 min -> 0 slots
    windows = [TimeInterval(540, 569)]
    target_date = date(2026, 8, 17)
    tz = "Asia/Kolkata"
    current_time = datetime(2026, 8, 1, 8, 0, tzinfo=ZoneInfo(tz))

    slots = SchedulingEngine.generate_discrete_slots(
        available_windows=windows,
        target_date=target_date,
        duration_minutes=30,
        current_time=current_time,
        tz_name=tz,
    )
    assert len(slots) == 0


def test_slot_generation_simulated_times():
    windows = [TimeInterval(540, 1020)]  # 09:00 - 17:00 (16 slots of 30 mins)
    today = date(2026, 8, 15)
    tz = "Asia/Kolkata"

    # Simulation 1: 08:00 (before schedule starts) -> All 16 slots available
    t_0800 = datetime(2026, 8, 15, 8, 0, tzinfo=ZoneInfo(tz))
    s1 = SchedulingEngine.generate_discrete_slots(windows, today, 30, current_time=t_0800, tz_name=tz)
    assert len(s1) == 16

    # Simulation 2: 10:20 (during morning) -> Slots starting >= 10:20 (10:30 onwards -> 13 slots)
    t_1020 = datetime(2026, 8, 15, 10, 20, tzinfo=ZoneInfo(tz))
    s2 = SchedulingEngine.generate_discrete_slots(windows, today, 30, current_time=t_1020, tz_name=tz)
    assert len(s2) == 13
    assert s2[0]["start_time"] == "10:30"

    # Simulation 3: 15:45 (afternoon) -> Slots starting >= 15:45 (16:00, 16:30 -> 2 slots)
    t_1545 = datetime(2026, 8, 15, 15, 45, tzinfo=ZoneInfo(tz))
    s3 = SchedulingEngine.generate_discrete_slots(windows, today, 30, current_time=t_1545, tz_name=tz)
    assert len(s3) == 2
    assert s3[0]["start_time"] == "16:00"
    assert s3[1]["start_time"] == "16:30"

    # Simulation 4: 23:59 (late night) -> 0 slots
    t_2359 = datetime(2026, 8, 15, 23, 59, tzinfo=ZoneInfo(tz))
    s4 = SchedulingEngine.generate_discrete_slots(windows, today, 30, current_time=t_2359, tz_name=tz)
    assert len(s4) == 0


def test_slot_generation_past_date_returns_empty():
    windows = [TimeInterval(540, 720)]  # 09:00 - 12:00
    past_date = date(2026, 8, 10)
    current_time = datetime(2026, 8, 15, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata"))

    slots = SchedulingEngine.generate_discrete_slots(
        available_windows=windows,
        target_date=past_date,
        duration_minutes=30,
        current_time=current_time,
        tz_name="Asia/Kolkata",
    )
    assert len(slots) == 0
