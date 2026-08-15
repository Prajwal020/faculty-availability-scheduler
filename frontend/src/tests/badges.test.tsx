import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge } from '../components/ui/Badge';

describe('Badge Component', () => {
  it('renders REQUESTED status with warning label', () => {
    render(<Badge status="REQUESTED" />);
    expect(screen.getByText('Requested')).toBeInTheDocument();
  });

  it('renders ACCEPTED status with success label', () => {
    render(<Badge status="ACCEPTED" />);
    expect(screen.getByText('Accepted')).toBeInTheDocument();
  });

  it('renders REJECTED status with danger label', () => {
    render(<Badge status="REJECTED" />);
    expect(screen.getByText('Rejected')).toBeInTheDocument();
  });

  it('renders CANCELLED status with cancelled label', () => {
    render(<Badge status="CANCELLED" />);
    expect(screen.getByText('Cancelled')).toBeInTheDocument();
  });

  it('renders meeting mode badges properly', () => {
    render(<Badge status="IN_PERSON" />);
    expect(screen.getByText('In Person')).toBeInTheDocument();
  });

  it('renders user status badges properly', () => {
    render(<Badge status="ACTIVE" />);
    expect(screen.getByText('Active')).toBeInTheDocument();
    render(<Badge status="SUSPENDED" />);
    expect(screen.getByText('Suspended')).toBeInTheDocument();
  });
});
