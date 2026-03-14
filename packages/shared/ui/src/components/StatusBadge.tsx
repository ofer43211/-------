import React from 'react';

export interface StatusBadgeProps {
  status: 'online' | 'offline' | 'error' | 'pending';
  label?: string;
}

const STATUS_LABELS: Record<StatusBadgeProps['status'], string> = {
  online: 'Online',
  offline: 'Offline',
  error: 'Error',
  pending: 'Pending',
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label }) => {
  return (
    <span data-component="status-badge" data-status={status}>
      {label ?? STATUS_LABELS[status]}
    </span>
  );
};
