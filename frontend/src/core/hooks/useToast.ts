import { useToastStore } from '@stores/toastStore';

export function useToast() {
  const { success, error, warning, info, addToast, removeToast, clearToasts } =
    useToastStore();

  return {
    success,
    error,
    warning,
    info,
    toast: addToast,
    dismiss: removeToast,
    clear: clearToasts,
  };
}

export default useToast;
