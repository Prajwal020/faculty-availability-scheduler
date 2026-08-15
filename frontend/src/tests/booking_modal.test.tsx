import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BookingModal } from '../components/appointments/BookingModal';
import { FacultyPublicProfile, BookableSlot } from '../types';
import { appointmentsApi } from '../api/appointments';

vi.mock('../api/appointments', () => ({
  appointmentsApi: {
    bookAppointment: vi.fn(),
  },
}));

const mockFaculty: FacultyPublicProfile = {
  id: 'faculty-123',
  user_id: 'user-123',
  full_name: 'Dr. Rajesh Sharma',
  email: 'prof.sharma@institution.edu',
  title: 'Professor & Head',
  office_location: 'Block A, Room 101',
  bio: 'Systems research',
  meeting_mode: 'IN_PERSON',
  department_id: 'dept-123',
  department_name: 'Computer Science',
  department_code: 'CS',
};

const mockSlot: BookableSlot = {
  start_datetime: '2026-08-24T09:00:00Z',
  end_datetime: '2026-08-24T09:30:00Z',
  start_time: '09:00',
  end_time: '09:30',
  duration_minutes: 30,
  status: 'AVAILABLE',
};

const renderWithQueryClient = (ui: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
};

describe('BookingModal Component', () => {
  it('renders slot time and faculty information accurately', () => {
    renderWithQueryClient(
      <BookingModal
        isOpen={true}
        onClose={() => {}}
        faculty={mockFaculty}
        date="2026-08-24"
        slot={mockSlot}
      />
    );

    expect(screen.getByText('Request Faculty Appointment')).toBeInTheDocument();
    expect(screen.getByText('Dr. Rajesh Sharma')).toBeInTheDocument();
    expect(screen.getByText(/9:00 AM – 9:30 AM IST/)).toBeInTheDocument();
  });

  it('validates agenda requirement before submission', async () => {
    renderWithQueryClient(
      <BookingModal
        isOpen={true}
        onClose={() => {}}
        faculty={mockFaculty}
        date="2026-08-24"
        slot={mockSlot}
      />
    );

    const submitBtn = screen.getByText('Confirm Request');
    fireEvent.click(submitBtn);

    expect(
      await screen.findByText('Please state the purpose or agenda for your appointment.')
    ).toBeInTheDocument();
  });

  it('displays user-friendly error message on 409 conflict', async () => {
    vi.mocked(appointmentsApi.bookAppointment).mockRejectedValueOnce({
      code: 'SLOT_UNAVAILABLE',
      message: 'The requested time slot is no longer available.',
    });

    renderWithQueryClient(
      <BookingModal
        isOpen={true}
        onClose={() => {}}
        faculty={mockFaculty}
        date="2026-08-24"
        slot={mockSlot}
      />
    );

    const textarea = screen.getByPlaceholderText(/Discuss capstone project thesis outline/);
    fireEvent.change(textarea, { target: { value: 'Discussion about thesis draft' } });

    const submitBtn = screen.getByText('Confirm Request');
    fireEvent.click(submitBtn);

    expect(
      await screen.findByText(
        'This slot was just booked or is no longer available. Please select another time slot.'
      )
    ).toBeInTheDocument();
  });
});
