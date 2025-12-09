/**
 * Enhanced Toast Hook for Devora
 * Provides a consistent API for showing notifications
 */

import { toast } from 'sonner';

type ToastType = 'success' | 'error' | 'warning' | 'info' | 'loading';

interface ToastOptions {
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
  cancel?: {
    label: string;
    onClick?: () => void;
  };
  id?: string;
  dismissible?: boolean;
}

interface PromiseToastMessages<T> {
  loading: string;
  success: string | ((data: T) => string);
  error: string | ((error: Error) => string);
}

export function useToast() {
  const showToast = (type: ToastType, message: string, options?: ToastOptions) => {
    const baseOptions = {
      duration: options?.duration ?? 4000,
      dismissible: options?.dismissible ?? true,
      id: options?.id,
      action: options?.action,
      cancel: options?.cancel,
    };

    switch (type) {
      case 'success':
        return toast.success(message, baseOptions);
      case 'error':
        return toast.error(message, baseOptions);
      case 'warning':
        return toast.warning(message, baseOptions);
      case 'info':
        return toast.info(message, baseOptions);
      case 'loading':
        return toast.loading(message, { ...baseOptions, duration: Infinity });
      default:
        return toast(message, baseOptions);
    }
  };

  const success = (message: string, options?: ToastOptions) =>
    showToast('success', message, options);

  const error = (message: string, options?: ToastOptions) =>
    showToast('error', message, { duration: 6000, ...options });

  const warning = (message: string, options?: ToastOptions) =>
    showToast('warning', message, options);

  const info = (message: string, options?: ToastOptions) =>
    showToast('info', message, options);

  const loading = (message: string, options?: ToastOptions) =>
    showToast('loading', message, options);

  const dismiss = (toastId?: string | number) => {
    if (toastId) {
      toast.dismiss(toastId);
    } else {
      toast.dismiss();
    }
  };

  // Promise-based toast for async operations
  const promise = <T,>(
    promiseOrFn: Promise<T> | (() => Promise<T>),
    messages: PromiseToastMessages<T>,
    options?: ToastOptions
  ) => {
    const actualPromise = typeof promiseOrFn === 'function' ? promiseOrFn() : promiseOrFn;

    return toast.promise(actualPromise, {
      loading: messages.loading,
      success: (data) =>
        typeof messages.success === 'function' ? messages.success(data) : messages.success,
      error: (err) =>
        typeof messages.error === 'function' ? messages.error(err) : messages.error,
      ...options,
    });
  };

  // Specialized toasts for common operations
  const saved = (filename?: string) =>
    success(filename ? `${filename} sauvegarde` : 'Sauvegarde effectuee');

  const deleted = (item?: string) =>
    success(item ? `${item} supprime` : 'Suppression effectuee');

  const created = (item?: string) =>
    success(item ? `${item} cree` : 'Creation effectuee');

  const copied = () => success('Copie dans le presse-papiers');

  const networkError = () =>
    error('Erreur de connexion. Verifiez votre connexion internet.', {
      action: {
        label: 'Reessayer',
        onClick: () => window.location.reload(),
      },
    });

  const unauthorized = () =>
    error('Session expiree. Veuillez vous reconnecter.', {
      action: {
        label: 'Se connecter',
        onClick: () => (window.location.href = '/login'),
      },
    });

  const validationError = (field?: string) =>
    warning(field ? `Le champ "${field}" est invalide` : 'Veuillez verifier les champs');

  return {
    // Base methods
    success,
    error,
    warning,
    info,
    loading,
    dismiss,
    promise,

    // Specialized methods
    saved,
    deleted,
    created,
    copied,
    networkError,
    unauthorized,
    validationError,

    // Raw toast access
    toast,
  };
}

// Export singleton for non-hook usage
export const toastService = {
  success: (message: string, options?: ToastOptions) =>
    toast.success(message, { duration: 4000, ...options }),
  error: (message: string, options?: ToastOptions) =>
    toast.error(message, { duration: 6000, ...options }),
  warning: (message: string, options?: ToastOptions) =>
    toast.warning(message, { duration: 4000, ...options }),
  info: (message: string, options?: ToastOptions) =>
    toast.info(message, { duration: 4000, ...options }),
  loading: (message: string, options?: ToastOptions) =>
    toast.loading(message, options),
  dismiss: (id?: string | number) => toast.dismiss(id),
};

export default useToast;
