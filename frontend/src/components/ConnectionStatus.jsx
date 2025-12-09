import * as React from 'react';
import { Wifi, WifiOff, RefreshCw, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function ConnectionStatus({
  className,
  showWhenConnected = false,
}) {
  const [state, setState] = React.useState('connected');
  const [isVisible, setIsVisible] = React.useState(false);
  const reconnectTimeoutRef = React.useRef(null);

  React.useEffect(() => {
    const handleOnline = () => {
      setState('connected');
      // Show briefly when reconnected
      setIsVisible(true);
      setTimeout(() => {
        if (!showWhenConnected) {
          setIsVisible(false);
        }
      }, 3000);
    };

    const handleOffline = () => {
      setState('disconnected');
      setIsVisible(true);
    };

    // Monitor connection
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Initial state
    if (!navigator.onLine) {
      setState('disconnected');
      setIsVisible(true);
    } else if (showWhenConnected) {
      setIsVisible(true);
    }

    // Monitor connection quality with Network Information API
    const connection = navigator.connection;
    if (connection) {
      const handleConnectionChange = () => {
        if (connection.effectiveType === '2g' || connection.effectiveType === 'slow-2g') {
          setState('slow');
          setIsVisible(true);
        } else if (navigator.onLine && state === 'slow') {
          setState('connected');
          if (!showWhenConnected) {
            setTimeout(() => setIsVisible(false), 3000);
          }
        }
      };

      connection.addEventListener('change', handleConnectionChange);
      return () => {
        connection.removeEventListener('change', handleConnectionChange);
      };
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [showWhenConnected, state]);

  // Listen for API errors that indicate connection issues
  React.useEffect(() => {
    const handleApiError = (event) => {
      if (event.detail.status === 0 || event.detail.status >= 500) {
        setState('reconnecting');
        setIsVisible(true);

        // Try to reconnect
        reconnectTimeoutRef.current = setTimeout(() => {
          if (navigator.onLine) {
            setState('connected');
            if (!showWhenConnected) {
              setTimeout(() => setIsVisible(false), 3000);
            }
          }
        }, 5000);
      }
    };

    window.addEventListener('devora:api-error', handleApiError);
    return () => {
      window.removeEventListener('devora:api-error', handleApiError);
    };
  }, [showWhenConnected]);

  if (!isVisible) return null;

  const statusConfig = {
    connected: {
      icon: Wifi,
      text: 'Connecte',
      bgColor: 'bg-green-500/10 border-green-500/20',
      textColor: 'text-green-400',
    },
    disconnected: {
      icon: WifiOff,
      text: 'Hors ligne',
      bgColor: 'bg-red-500/10 border-red-500/20',
      textColor: 'text-red-400',
    },
    reconnecting: {
      icon: RefreshCw,
      text: 'Reconnexion...',
      bgColor: 'bg-yellow-500/10 border-yellow-500/20',
      textColor: 'text-yellow-400',
      animate: true,
    },
    slow: {
      icon: AlertTriangle,
      text: 'Connexion lente',
      bgColor: 'bg-orange-500/10 border-orange-500/20',
      textColor: 'text-orange-400',
    },
  };

  const config = statusConfig[state];
  const Icon = config.icon;

  return (
    <div
      className={cn(
        'fixed bottom-4 right-4 z-50 flex items-center gap-2 px-3 py-2 rounded-lg border backdrop-blur-sm transition-all duration-300',
        config.bgColor,
        className
      )}
    >
      <Icon
        className={cn(
          'w-4 h-4',
          config.textColor,
          config.animate && 'animate-spin'
        )}
      />
      <span className={cn('text-sm font-medium', config.textColor)}>
        {config.text}
      </span>
    </div>
  );
}

// Minimal inline indicator for navbar
export function ConnectionIndicator({ className }) {
  const [isOnline, setIsOnline] = React.useState(navigator.onLine);

  React.useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <div
      className={cn(
        'w-2 h-2 rounded-full',
        isOnline ? 'bg-green-500' : 'bg-red-500',
        !isOnline && 'animate-pulse',
        className
      )}
      title={isOnline ? 'Connecte' : 'Hors ligne'}
    />
  );
}
