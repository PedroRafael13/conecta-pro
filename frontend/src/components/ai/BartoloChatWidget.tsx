'use client';

/**
 * Bartolo Chat Widget - Assistente IA Conversacional
 * Widget embedded que pode ser usado em páginas específicas
 */

import { MessageSquare, X, Send, ThumbsUp, ThumbsDown, Loader2, User } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
;
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { useBartoloChat } from '@/hooks/ai/useBartolo';
import { toast } from 'sonner';
import { ActionConfirmationModal } from './ActionConfirmationModal';

// Componente SVG do Dachshund (Cachorro Salsicha)
function DachshundIcon({ className = 'w-6 h-6' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 64 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <ellipse cx="32" cy="24" rx="22" ry="10" fill="#D2691E" stroke="#8B4513" strokeWidth="1.5" />
      <ellipse cx="50" cy="22" rx="8" ry="7" fill="#D2691E" stroke="#8B4513" strokeWidth="1.5" />
      <ellipse cx="56" cy="23" rx="4" ry="3.5" fill="#A0522D" stroke="#8B4513" strokeWidth="1" />
      <circle cx="58" cy="23" r="1.5" fill="#000" />
      <ellipse cx="48" cy="16" rx="3" ry="6" fill="#A0522D" stroke="#8B4513" strokeWidth="1" transform="rotate(-15 48 16)" />
      <ellipse cx="52" cy="16" rx="3" ry="6" fill="#A0522D" stroke="#8B4513" strokeWidth="1" transform="rotate(15 52 16)" />
      <circle cx="52" cy="20" r="1.5" fill="#000" />
      <rect x="18" y="32" width="2.5" height="8" rx="1.25" fill="#8B4513" />
      <rect x="26" y="32" width="2.5" height="8" rx="1.25" fill="#8B4513" />
      <rect x="38" y="32" width="2.5" height="8" rx="1.25" fill="#8B4513" />
      <rect x="46" y="32" width="2.5" height="8" rx="1.25" fill="#8B4513" />
      <ellipse cx="19.25" cy="41" rx="2" ry="1.5" fill="#A0522D" />
      <ellipse cx="27.25" cy="41" rx="2" ry="1.5" fill="#A0522D" />
      <ellipse cx="39.25" cy="41" rx="2" ry="1.5" fill="#A0522D" />
      <ellipse cx="47.25" cy="41" rx="2" ry="1.5" fill="#A0522D" />
      <path d="M 10 20 Q 8 18 6 20 Q 4 22 5 24" stroke="#8B4513" strokeWidth="2.5" fill="none" strokeLinecap="round" />
    </svg>
  );
}

// Types
export interface ActionPreview {
  action_id: string;
  action_type: string;
  title: string;
  description: string;
  affected_entities: Array<{
    type: string;
    id: string;
    name?: string;
  }>;
  changes_summary: string[];
  warnings: string[];
  required_permission: string;
  user_has_permission: boolean;
  parameters: Record<string, unknown>;
  can_be_undone: boolean;
  requires_confirmation: boolean;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  data_results?: any;
  suggestions?: string[];
}

interface BartoloChatWidgetProps {
  module?: string;
  initialOpen?: boolean;
}

export function BartoloChatWidget({
  module,
  initialOpen = false,
}: BartoloChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(initialOpen);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sessionId] = useState(() => BartoloService.generateSessionId());
  const [actionPreview, setActionPreview] = useState<ActionPreview | null>(null);
  const [isExecutingAction, setIsExecutingAction] = useState(false);
  const [currentUserId] = useState(1); // TODO: Get from auth context
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const {
    greeting,
    isLoadingGreeting,
    sendMessage,
    isSending,
    lastResponse,
    submitFeedback,
    suggestions,
  } = useBartoloChat(sessionId, module);

  // Adiciona greeting quando carrega
  useEffect(() => {
    if (greeting && messages.length === 0) {
      setMessages([
        {
          id: 'greeting',
          role: 'assistant',
          content: greeting,
          timestamp: new Date(),
        },
      ]);
    }
  }, [greeting]);

  // Adiciona resposta do Bartolo quando recebe
  useEffect(() => {
    if (lastResponse) {
      // Verifica se há action_preview (ação detectada)
      const responseWithPreview = lastResponse as typeof lastResponse & { action_preview?: ActionPreview };

      if (responseWithPreview.action_preview) {
        setActionPreview(responseWithPreview.action_preview);
      }

      setMessages((prev) => [
        ...prev,
        {
          id: lastResponse.message_id,
          role: 'assistant',
          content: lastResponse.response,
          timestamp: new Date(),
          data_results: lastResponse.data_results,
          suggestions: (lastResponse.suggestions as string[]) || undefined,
        },
      ]);
    }
  }, [lastResponse]);

  // Auto-scroll para última mensagem
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Foca input quando abre
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleSend = async () => {
    if (!input.trim() || isSending) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    try {
      await sendMessage({
        message: input.trim(),
        session_id: sessionId,
        module: module,
      });
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
    inputRef.current?.focus();
  };

  const handleFeedback = (messageId: string, isPositive: boolean) => {
    submitFeedback({
      interaction_id: messageId,
      feedback_type: isPositive ? 'helpful' : 'not_helpful',
    });
  };

  const handleConfirmAction = async () => {
    if (!actionPreview) return;

    setIsExecutingAction(true);

    try {
      const result = await BartoloService.confirmAction(
        currentUserId,
        actionPreview.action_id,
        true
      );

      // Adiciona resultado da execução nas mensagens
      setMessages((prev) => [
        ...prev,
        {
          id: result.message_id,
          role: 'assistant',
          content: result.response,
          timestamp: new Date(),
        },
      ]);

      toast.success('Ação executada com sucesso!');
      setActionPreview(null);
    } catch (error) {
      console.error('Error executing action:', error);
      toast.error('Erro ao executar ação. Tente novamente.');
    } finally {
      setIsExecutingAction(false);
    }
  };

  const handleCancelAction = async () => {
    if (!actionPreview) return;

    try {
      await BartoloService.confirmAction(
        currentUserId,
        actionPreview.action_id,
        false
      );

      toast.info('Ação cancelada');
      setActionPreview(null);
    } catch (error) {
      console.error('Error canceling action:', error);
      setActionPreview(null);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className={cn(
          'fixed bottom-6 right-6 z-50',
          'w-16 h-16 rounded-full',
          'bg-gradient-to-br from-amber-500 via-amber-600 to-orange-600',
          'hover:from-amber-400 hover:via-amber-500 hover:to-orange-500',
          'shadow-2xl shadow-amber-500/40 hover:shadow-amber-400/50',
          'flex items-center justify-center',
          'transition-all duration-300',
          'hover:scale-110 active:scale-95',
          'ring-4 ring-amber-400/20 hover:ring-amber-300/30',
          'group'
        )}
        aria-label="Abrir chat com Bartolo"
      >
        <DachshundIcon className="w-9 h-9" />
      </button>
    );
  }

  return (
    <>
    <div className="fixed bottom-6 right-6 z-50 flex h-[38rem] w-[28rem] flex-col bg-gradient-to-br from-slate-900/95 via-slate-900/98 to-slate-950/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-amber-500/20 hover:border-amber-400/30 transition-all duration-300 overflow-hidden animate-in fade-in slide-in-from-bottom-8 zoom-in-95">
      {/* Header */}
      <div className="relative flex items-center justify-between px-5 py-4 bg-gradient-to-r from-amber-600 via-amber-500 to-orange-500 overflow-hidden">
        {/* Background pattern */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(255,255,255,0.1),transparent)] pointer-events-none" />

        <div className="flex items-center gap-3 relative z-10">
          <div className="w-11 h-11 rounded-full bg-white/25 backdrop-blur-sm flex items-center justify-center ring-2 ring-white/30 shadow-lg">
            <DachshundIcon className="w-7 h-7" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-white tracking-tight">Bartolo</h3>
              <span className="w-2 h-2 rounded-full bg-green-400 shadow-lg shadow-green-400/50 animate-pulse" />
            </div>
            <p className="text-xs text-white/90 font-medium">
              Assistente IA • Online
            </p>
          </div>
        </div>

        <button
          onClick={() => setIsOpen(false)}
          className="p-2 rounded-xl hover:bg-white/20 active:bg-white/30 transition-all duration-200 group relative z-10"
          title="Fechar"
        >
          <X className="w-5 h-5 text-white group-hover:rotate-90 transition-transform duration-300" />
        </button>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-5 scrollbar-thin scrollbar-thumb-amber-500/20 scrollbar-track-transparent" ref={scrollRef}>
        <div className="space-y-4">
          {isLoadingGreeting && (
            <div className="flex items-center gap-2.5 text-sm text-amber-400/80 animate-in fade-in">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Bartolo está se preparando...</span>
            </div>
          )}

          {messages.map((message, idx) => (
            <div
              key={message.id}
              className={cn(
                'flex gap-2.5 animate-in fade-in slide-in-from-bottom-4',
                message.role === 'user' ? 'flex-row-reverse' : ''
              )}
              style={{ animationDelay: `${idx * 50}ms` }}
            >
              {message.role === 'user' ? (
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 flex-shrink-0 flex items-center justify-center ring-2 ring-slate-600/50 shadow-lg">
                  <User className="w-4 h-4 text-slate-300" />
                </div>
              ) : (
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-amber-500/30 to-orange-500/20 flex-shrink-0 flex items-center justify-center ring-2 ring-amber-500/20 shadow-lg">
                  <DachshundIcon className="w-5 h-5" />
                </div>
              )}

              <div
                className={cn(
                  'flex max-w-[82%] flex-col gap-2',
                  message.role === 'user' ? 'items-end' : ''
                )}
              >
                <div
                  className={cn(
                    'rounded-2xl px-4 py-3 shadow-lg transition-all duration-200 hover:shadow-xl',
                    message.role === 'user'
                      ? 'bg-gradient-to-br from-amber-500 to-amber-600 text-white rounded-br-sm'
                      : 'bg-slate-800/80 backdrop-blur-sm text-slate-100 rounded-bl-sm border border-slate-700/50'
                  )}
                >
                  <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                </div>

                {/* Data Results */}
                {message.data_results && (
                  <div className="w-full rounded-xl border border-amber-500/30 bg-gradient-to-br from-amber-500/10 to-orange-500/5 backdrop-blur-sm p-3.5 text-xs shadow-lg">
                    <div className="font-bold mb-1.5 text-amber-300 flex items-center gap-2">
                      <span className="text-base">📊</span>
                      {message.data_results.entity}
                    </div>
                    <div className="text-slate-400 font-medium">
                      {message.data_results.total_count} registros encontrados
                    </div>
                  </div>
                )}

                {/* Suggestions from message */}
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {message.suggestions.map((sug, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSuggestionClick(sug)}
                        className="text-xs px-3 py-1.5 rounded-xl bg-slate-800/60 backdrop-blur-sm text-slate-300 hover:bg-gradient-to-r hover:from-amber-500/20 hover:to-orange-500/20 hover:text-amber-300 transition-all duration-200 border border-slate-700/50 hover:border-amber-500/40 shadow-sm hover:shadow-lg hover:shadow-amber-500/10 font-medium"
                      >
                        {sug}
                      </button>
                    ))}
                  </div>
                )}

                {/* Feedback buttons */}
                {message.role === 'assistant' && message.id !== 'greeting' && (
                  <div className="flex gap-1.5 opacity-60 hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => handleFeedback(message.id, true)}
                      className="p-1.5 rounded-lg hover:bg-green-500/20 active:bg-green-500/30 transition-all group"
                      title="Útil"
                    >
                      <ThumbsUp className="w-3.5 h-3.5 text-slate-500 group-hover:text-green-400 transition-colors" />
                    </button>
                    <button
                      onClick={() => handleFeedback(message.id, false)}
                      className="p-1.5 rounded-lg hover:bg-red-500/20 active:bg-red-500/30 transition-all group"
                      title="Não ajudou"
                    >
                      <ThumbsDown className="w-3.5 h-3.5 text-slate-500 group-hover:text-red-400 transition-colors" />
                    </button>
                  </div>
                )}

                <span className="text-xs text-muted-foreground">
                  {message.timestamp.toLocaleTimeString('pt-BR', {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </span>
              </div>
            </div>
          ))}

          {isSending && (
            <div className="flex gap-2.5 items-start animate-in fade-in slide-in-from-bottom-4">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-amber-500/30 to-orange-500/20 flex-shrink-0 flex items-center justify-center ring-2 ring-amber-500/20 shadow-lg animate-pulse">
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
          )}
        </div>
      </ScrollArea>

      {/* Suggestions */}
      {messages.length <= 1 && suggestions.length > 0 && (
        <div className="border-t border-slate-700/30 bg-slate-900/50 backdrop-blur-sm p-4 animate-in fade-in slide-in-from-bottom-4 delay-300">
          <p className="mb-2.5 text-xs font-semibold text-amber-400/80 flex items-center gap-2">
            <span className="w-1 h-1 rounded-full bg-amber-400 animate-pulse" />
            Sugestões rápidas
          </p>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => handleSuggestionClick(suggestion)}
                className="text-xs px-3.5 py-2 rounded-xl bg-slate-800/60 backdrop-blur-sm text-slate-300 hover:bg-gradient-to-r hover:from-amber-500/20 hover:to-orange-500/20 hover:text-amber-300 transition-all duration-200 border border-slate-700/50 hover:border-amber-500/40 shadow-sm hover:shadow-lg hover:shadow-amber-500/10 font-medium"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="border-t border-slate-700/30 bg-slate-900/50 backdrop-blur-sm p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex gap-2.5"
        >
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Digite sua mensagem..."
            disabled={isSending}
            className={cn(
              'flex-1 bg-slate-800/80 backdrop-blur-sm rounded-2xl px-4 py-3',
              'text-sm text-slate-100 placeholder:text-slate-500',
              'border border-slate-700/50',
              'focus:outline-none focus:ring-2 focus:ring-amber-500/60 focus:border-amber-500/60 focus:bg-slate-800',
              'transition-all duration-200',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          />
          <button
            type="submit"
            disabled={isSending || !input.trim()}
            className={cn(
              'w-11 h-11 rounded-2xl',
              'bg-gradient-to-br from-amber-500 to-amber-600',
              'hover:from-amber-400 hover:to-amber-500',
              'shadow-lg shadow-amber-500/25 hover:shadow-amber-400/40',
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
        </form>
      </div>
    </div>

    {/* Modal de confirmação de ação */}
    {actionPreview && (
      <ActionConfirmationModal
        preview={actionPreview}
        onConfirm={handleConfirmAction}
        onCancel={handleCancelAction}
        isExecuting={isExecutingAction}
      />
    )}
    </>
  );
}
