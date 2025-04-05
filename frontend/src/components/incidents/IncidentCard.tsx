import React from 'react';
import Card from '../ui/Card';
import PriorityBadge from './PriorityBadge';
import { InterpretationResult } from '../../types/api';

interface IncidentCardProps {
  incident: {
    id: string;
    interpretation: InterpretationResult;
    timestamp: string;
    status: 'pending' | 'processing' | 'verified' | 'dispatched';
  };
  onClick?: () => void;
  className?: string;
}

export const IncidentCard: React.FC<IncidentCardProps> = ({
  incident,
  onClick,
  className = '',
}) => {
  const { id, interpretation, timestamp, status } = incident;
  const { incident_type, address, priority, needs_verification } = interpretation;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs">Pending</span>;
      case 'processing':
        return <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">Processing</span>;
      case 'verified':
        return <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">Verified</span>;
      case 'dispatched':
        return <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs">Dispatched</span>;
      default:
        return null;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Card
      className={`hover:border-blue-300 transition-all duration-200 ${className}`}
      variant="bordered"
      onClick={onClick}
    >
      <div className="flex flex-col gap-2">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{incident_type}</h3>
            <p className="text-gray-600 text-sm mt-1">{address}</p>
          </div>
          <PriorityBadge priority={priority} />
        </div>
        
        <div className="flex justify-between mt-2">
          <div className="text-xs text-gray-500">
            <span className="font-medium">ID:</span> {id.slice(0, 8)}...
          </div>
          <div className="text-xs text-gray-500">
            {formatDate(timestamp)}
          </div>
        </div>
        
        <div className="flex justify-between items-center pt-2 mt-2 border-t border-gray-100">
          {getStatusBadge(status)}
          
          {needs_verification && (
            <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs">
              Needs Verification
            </span>
          )}
        </div>
      </div>
    </Card>
  );
};

export default IncidentCard; 