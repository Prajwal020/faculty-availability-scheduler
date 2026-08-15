import { describe, it, expect } from 'vitest';
import {
  getDayName,
  formatTime24to12,
  formatTimeRange,
  addDays,
} from '../utils/formatters';

describe('Date & Time Formatter Utilities', () => {
  it('correctly maps day numbers to day names (0=Monday)', () => {
    expect(getDayName(0)).toBe('Monday');
    expect(getDayName(6)).toBe('Sunday');
    expect(getDayName(0, true)).toBe('Mon');
    expect(getDayName(4, true)).toBe('Fri');
  });

  it('converts 24-hour time to 12-hour AM/PM format', () => {
    expect(formatTime24to12('09:00:00')).toBe('9:00 AM');
    expect(formatTime24to12('12:00:00')).toBe('12:00 PM');
    expect(formatTime24to12('13:30:00')).toBe('1:30 PM');
    expect(formatTime24to12('17:45')).toBe('5:45 PM');
  });

  it('formats time ranges correctly', () => {
    expect(formatTimeRange('09:00', '09:30')).toBe('9:00 AM – 9:30 AM');
    expect(formatTimeRange('14:00:00', '15:30:00')).toBe('2:00 PM – 3:30 PM');
  });

  it('adds calendar days accurately without timezone drift', () => {
    expect(addDays('2026-08-15', 2)).toBe('2026-08-17');
    expect(addDays('2026-08-31', 1)).toBe('2026-09-01');
  });
});
