import React from 'react';

interface CardProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  className?: string;
  headerAction?: React.ReactNode;
  footer?: React.ReactNode;
  variant?: 'default' | 'bordered' | 'elevated';
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({
  children,
  title,
  subtitle,
  className = '',
  headerAction,
  footer,
  variant = 'default',
  onClick,
}) => {
  const variantStyles = {
    default: 'bg-white',
    bordered: 'bg-white border border-gray-200',
    elevated: 'bg-white shadow-md',
  };

  return (
    <div 
      className={`
        ${variantStyles[variant]}
        rounded-lg overflow-hidden
        ${onClick ? 'cursor-pointer transition-all duration-200 hover:shadow-md' : ''}
        ${className}
      `}
      onClick={onClick}
    >
      {(title || subtitle || headerAction) && (
        <div className="px-4 py-3 border-b border-gray-100 flex justify-between items-center">
          <div>
            {title && <h3 className="text-lg font-semibold text-gray-800">{title}</h3>}
            {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
          </div>
          {headerAction && <div>{headerAction}</div>}
        </div>
      )}
      
      <div className="p-4">
        {children}
      </div>
      
      {footer && (
        <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card; 