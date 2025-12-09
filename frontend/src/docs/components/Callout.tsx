import React from 'react';
import { AlertCircle, AlertTriangle, Info, CheckCircle, Lightbulb } from 'lucide-react';

type CalloutType = 'info' | 'warning' | 'error' | 'success' | 'tip';

interface CalloutProps {
  type?: CalloutType;
  title?: string;
  children: React.ReactNode;
}

const calloutConfig = {
  info: {
    icon: Info,
    className: 'bg-blue-50 border-blue-200 text-blue-900',
    iconClassName: 'text-blue-500',
    titleClassName: 'text-blue-900'
  },
  warning: {
    icon: AlertTriangle,
    className: 'bg-yellow-50 border-yellow-200 text-yellow-900',
    iconClassName: 'text-yellow-500',
    titleClassName: 'text-yellow-900'
  },
  error: {
    icon: AlertCircle,
    className: 'bg-red-50 border-red-200 text-red-900',
    iconClassName: 'text-red-500',
    titleClassName: 'text-red-900'
  },
  success: {
    icon: CheckCircle,
    className: 'bg-green-50 border-green-200 text-green-900',
    iconClassName: 'text-green-500',
    titleClassName: 'text-green-900'
  },
  tip: {
    icon: Lightbulb,
    className: 'bg-purple-50 border-purple-200 text-purple-900',
    iconClassName: 'text-purple-500',
    titleClassName: 'text-purple-900'
  }
};

export const Callout: React.FC<CalloutProps> = ({
  type = 'info',
  title,
  children
}) => {
  const config = calloutConfig[type];
  const Icon = config.icon;

  return (
    <div className={`my-4 p-4 rounded-lg border ${config.className}`}>
      <div className="flex gap-3">
        <div className="flex-shrink-0">
          <Icon className={`w-5 h-5 ${config.iconClassName}`} />
        </div>
        <div className="flex-1">
          {title && (
            <h5 className={`font-semibold mb-1 ${config.titleClassName}`}>
              {title}
            </h5>
          )}
          <div className="text-sm leading-relaxed">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Callout;
