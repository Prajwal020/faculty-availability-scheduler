import React from 'react';
import { cn } from '../../utils/cn';
import {
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  MinusCircle,
  Building2,
  Video,
  Users,
} from 'lucide-react';
import { AppointmentStatus, MeetingMode, UserStatus } from '../../types';

interface BadgeProps {
  status?: AppointmentStatus | MeetingMode | UserStatus | string;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  size?: 'sm' | 'md';
  children?: React.ReactNode;
  className?: string;
  showIcon?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  status,
  variant,
  size = 'md',
  children,
  className,
  showIcon = true,
}) => {
  let badgeVariant = variant || 'default';
  let label = children;
  let icon: React.ReactNode = null;

  if (status) {
    switch (status) {
      // Appointment Statuses
      case 'REQUESTED':
        badgeVariant = 'warning';
        label = label || 'Requested';
        icon = <Clock className="w-3.5 h-3.5" />;
        break;
      case 'ACCEPTED':
        badgeVariant = 'success';
        label = label || 'Accepted';
        icon = <CheckCircle2 className="w-3.5 h-3.5" />;
        break;
      case 'REJECTED':
        badgeVariant = 'danger';
        label = label || 'Rejected';
        icon = <XCircle className="w-3.5 h-3.5" />;
        break;
      case 'CANCELLED':
        badgeVariant = 'neutral';
        label = label || 'Cancelled';
        icon = <MinusCircle className="w-3.5 h-3.5" />;
        break;
      case 'COMPLETED':
        badgeVariant = 'info';
        label = label || 'Completed';
        icon = <CheckCircle2 className="w-3.5 h-3.5" />;
        break;
      case 'RESCHEDULE_PROPOSED':
        badgeVariant = 'warning';
        label = label || 'Reschedule Proposed';
        icon = <AlertCircle className="w-3.5 h-3.5" />;
        break;

      // Meeting Modes
      case 'IN_PERSON':
        badgeVariant = 'neutral';
        label = label || 'In Person';
        icon = <Building2 className="w-3.5 h-3.5" />;
        break;
      case 'VIRTUAL':
        badgeVariant = 'info';
        label = label || 'Virtual';
        icon = <Video className="w-3.5 h-3.5" />;
        break;
      case 'HYBRID':
        badgeVariant = 'neutral';
        label = label || 'Hybrid';
        icon = <Users className="w-3.5 h-3.5" />;
        break;

      // User Statuses
      case 'ACTIVE':
        badgeVariant = 'success';
        label = label || 'Active';
        icon = <CheckCircle2 className="w-3.5 h-3.5" />;
        break;
      case 'SUSPENDED':
        badgeVariant = 'warning';
        label = label || 'Suspended';
        icon = <AlertCircle className="w-3.5 h-3.5" />;
        break;
      case 'DEACTIVATED':
        badgeVariant = 'danger';
        label = label || 'Deactivated';
        icon = <XCircle className="w-3.5 h-3.5" />;
        break;

      default:
        badgeVariant = badgeVariant || 'default';
        label = label || status;
    }
  }

  const variants = {
    default: 'bg-slate-100 text-slate-800 border-slate-200',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    warning: 'bg-amber-50 text-amber-800 border-amber-200',
    danger: 'bg-rose-50 text-rose-700 border-rose-200',
    info: 'bg-blue-50 text-blue-700 border-blue-200',
    neutral: 'bg-slate-100 text-slate-600 border-slate-200',
  };

  const sizes = {
    sm: 'text-[11px] px-2 py-0.5 gap-1 font-medium',
    md: 'text-xs px-2.5 py-1 gap-1.5 font-medium',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border shadow-xs select-none',
        variants[badgeVariant],
        sizes[size],
        className
      )}
    >
      {showIcon && icon && <span className="shrink-0">{icon}</span>}
      <span>{label}</span>
    </span>
  );
};
