import React from 'react';
import Badge from '../ui/Badge';

// Priority levels
// 1 - High (Urgent) - Red
// 2 - Medium - Orange
// 3 - Low - Yellow
// 4 - Informational - Blue
// 5 - Non-Emergency - Green

interface PriorityBadgeProps {
  priority: number;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({
  priority,
  showLabel = true,
  size = 'md',
  className = '',
}) => {
  const getPriorityLabel = (priority: number): string => {
    switch (priority) {
      case 1: return 'High';
      case 2: return 'Medium';
      case 3: return 'Low';
      case 4: return 'Info';
      case 5: return 'Non-Emergency';
      default: return 'Unknown';
    }
  };

  const getPriorityVariant = (priority: number): 'danger' | 'warning' | 'success' | 'info' | 'primary' => {
    switch (priority) {
      case 1: return 'danger';
      case 2: return 'warning';
      case 3: return 'warning';
      case 4: return 'info';
      case 5: return 'success';
      default: return 'primary';
    }
  };

  return (
    <Badge 
      variant={getPriorityVariant(priority)} 
      size={size} 
      withDot 
      className={className}
    >
      {showLabel ? getPriorityLabel(priority) : `P${priority}`}
    </Badge>
  );
};

export default PriorityBadge; 