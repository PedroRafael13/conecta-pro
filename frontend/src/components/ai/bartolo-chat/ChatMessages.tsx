import { forwardRef } from 'react';
import { User, ThumbsUp, ThumbsDown } from 'lucide-react';
import DOMPurify from 'dompurify';
import { cn } from '@/lib/utils';
import { DachshundIcon } from './DachshundIcon';
import type { BartoloMessage, BartoloAction } from './types';

interface ChatMessagesProps {
  messages: BartoloMessage[];
  isSending: boolean;
  onFeedback: (messageId: string, isPositive: boolean) => void;
  onActionClick: (action: BartoloAction) => void;
}

export const ChatMessages = forwardRef<HTMLDivElement, ChatMessagesProps>(
  function ChatMessages({ messages, isSending, onFeedback, onActionClick }, ref) {
    return (
      <div className="flex-1 overflow-y-auto p-5 space-y-4 scrollbar-thin scrollbar-thumb-amber-500/20 scrollbar-track-transparent">
        {messages.length === 0 ? (
          <EmptyState />
        ) : (
          messages.map((msg, idx) => (
            <MessageBubble
              key={msg.id}
              message={msg}
              index={idx}
              onFeedback={onFeedback}
              onActionClick={onActionClick}
            />
          ))
        )}

        {isSending && <TypingIndicator />}

        <div ref={ref} />
      </div>
    );
  }
);

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center animate-in fade-in duration-500">
      <div className="w-24 h-24 rounded-full bg-gradient-to-br from-amber-500/20 to-orange-500/10 flex items-center justify-center mb-5 ring-4 ring-amber-500/10 shadow-xl">
        <DachshundIcon className="w-14 h-14 animate-in zoom-in duration-700" />
      </div>
      <h4 className="text-base font-bold text-slate-100 mb-2 bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">
        Ola! Sou o Bartolo
      </h4>
      <p className="text-sm text-slate-400 max-w-[240px] leading-relaxed">
        Seu assistente IA do Conecta PRO. Como posso ajudar voce hoje?
      </p>
    </div>
  );
}

function MessageBubble({
  message,
  index,
  onFeedback,
  onActionClick,
}: {
  message: BartoloMessage;
  index: number;
  onFeedback: (messageId: string, isPositive: boolean) => void;
  onActionClick: (action: BartoloAction) => void;
}) {
  return (
    <div
      className={cn(
        'flex gap-2.5 animate-in fade-in slide-in-from-bottom-4',
        message.role === 'user' ? 'justify-end' : 'justify-start'
      )}
      style={{ animationDelay: `${index * 50}ms` }}
    >
      {message.role === 'assistant' && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-500/30 to-orange-500/20 flex-shrink-0 flex items-center justify-center ring-2 ring-amber-500/20 shadow-lg">
          <DachshundIcon className="w-5 h-5" />
        </div>
      )}
      <div
        className={cn(
          'max-w-[82%] rounded-2xl px-4 py-3 shadow-lg',
          'transition-all duration-200 hover:shadow-xl',
          message.role === 'user'
            ? 'bg-gradient-to-br from-navy-600 to-navy-700 text-white rounded-br-sm'
            : 'bg-slate-800/80 backdrop-blur-sm text-slate-100 rounded-bl-sm border border-slate-700/50'
        )}
      >
        {message.contentHtml ? (
          <div
            className="text-sm prose prose-invert prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(message.contentHtml) }}
          />
        ) : (
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        )}

        {message.actions && message.actions.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {message.actions.map((action, idx) => (
              <button
                key={idx}
                onClick={() => onActionClick(action)}
                className="text-xs px-3 py-1.5 rounded-full bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-amber-300 hover:from-amber-500/30 hover:to-orange-500/30 hover:text-amber-200 transition-all duration-200 border border-amber-500/30 hover:border-amber-400/50 shadow-sm hover:shadow-amber-500/20 font-medium"
              >
                {action.label}
              </button>
            ))}
          </div>
        )}

        {message.role === 'assistant' && (
          <div className="mt-2.5 flex gap-1.5 opacity-60 hover:opacity-100 transition-opacity">
            <button
              onClick={() => onFeedback(message.id, true)}
              className="p-1.5 rounded-lg hover:bg-green-500/20 active:bg-green-500/30 transition-all group"
              title="Util"
            >
              <ThumbsUp className="w-3.5 h-3.5 text-slate-500 group-hover:text-green-400 transition-colors" />
            </button>
            <button
              onClick={() => onFeedback(message.id, false)}
              className="p-1.5 rounded-lg hover:bg-red-500/20 active:bg-red-500/30 transition-all group"
              title="Nao ajudou"
            >
              <ThumbsDown className="w-3.5 h-3.5 text-slate-500 group-hover:text-red-400 transition-colors" />
            </button>
          </div>
        )}
      </div>
      {message.role === 'user' && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 flex-shrink-0 flex items-center justify-center ring-2 ring-slate-600/50 shadow-lg">
          <User className="w-4 h-4 text-slate-300" />
        </div>
      )}
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex gap-2.5 items-start animate-in fade-in slide-in-from-bottom-4">
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-500/30 to-orange-500/20 flex-shrink-0 flex items-center justify-center ring-2 ring-amber-500/20 shadow-lg animate-pulse">
        <DachshundIcon className="w-5 h-5" />
      </div>
      <div className="bg-slate-800/80 backdrop-blur-sm border border-slate-700/50 rounded-2xl rounded-bl-sm px-5 py-3.5 shadow-lg">
        <div className="flex gap-1.5">
          <span className="w-2.5 h-2.5 bg-gradient-to-r from-amber-400 to-orange-400 rounded-full animate-bounce [animation-delay:-0.3s] shadow-lg shadow-amber-400/50" />
          <span className="w-2.5 h-2.5 bg-gradient-to-r from-amber-400 to-orange-400 rounded-full animate-bounce [animation-delay:-0.15s] shadow-lg shadow-amber-400/50" />
          <span className="w-2.5 h-2.5 bg-gradient-to-r from-amber-400 to-orange-400 rounded-full animate-bounce shadow-lg shadow-amber-400/50" />
        </div>
      </div>
    </div>
  );
}
