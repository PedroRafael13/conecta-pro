import { forwardRef } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  value: string;
  isSending: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
}

export const ChatInput = forwardRef<HTMLInputElement, ChatInputProps>(
  function ChatInput({ value, isSending, onChange, onSubmit }, ref) {
    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      onSubmit();
    };

    return (
      <form onSubmit={handleSubmit} className="p-4 border-t border-slate-700/30 bg-slate-900/50 backdrop-blur-sm">
        <div className="flex gap-2.5">
          <input
            ref={ref}
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Digite sua mensagem..."
            disabled={isSending}
            className={cn(
              'flex-1 bg-slate-800/80 backdrop-blur-sm rounded-2xl px-4 py-3',
              'text-sm text-slate-100 placeholder:text-slate-500',
              'border border-slate-700/50',
              'focus:outline-none focus:ring-2 focus:ring-brand-500/60 focus:border-brand-500/60 focus:bg-slate-800',
              'transition-all duration-200',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          />
          <button
            type="submit"
            disabled={!value.trim() || isSending}
            className={cn(
              'w-11 h-11 rounded-2xl',
              'bg-gradient-to-br from-brand-500 to-brand-600',
              'hover:from-brand-400 hover:to-brand-500',
              'shadow-lg shadow-brand-500/25 hover:shadow-brand-400/40',
              'flex items-center justify-center',
              'transition-all duration-200',
              'hover:scale-105 active:scale-95',
              'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:shadow-none'
            )}
          >
            {isSending ? (
              <Loader2 className="w-5 h-5 text-white animate-spin" />
            ) : (
              <Send className="w-5 h-5 text-white" />
            )}
          </button>
        </div>
      </form>
    );
  }
);
