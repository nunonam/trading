interface ToastItem {
  id: number;
  message: string;
}

interface ToastProps {
  toasts: ToastItem[];
  onRemove: (id: number) => void;
}

export default function Toast({ toasts, onRemove }: ToastProps) {
  if (toasts.length === 0) return null;

  return (
    <div className="toast-container">
      {toasts.map((t) => (
        <div key={t.id} className="toast toast-error">
          <span className="toast-message">{t.message}</span>
          <button className="toast-close" onClick={() => onRemove(t.id)}>
            &times;
          </button>
        </div>
      ))}
    </div>
  );
}
