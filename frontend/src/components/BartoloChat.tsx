'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useBartoloChat } from '@/hooks/ai/useBartolo';
import { BartoloService } from '@/services/ai/bartolo.service';
import { ActionConfirmationModal } from '@/components/ai/ActionConfirmationModal';
import { useAuth } from '@/hooks/useAuth';
import {
  DachshundIcon,
  ChatHeader,
  ChatMessages,
  ChatSuggestions,
  ChatInput,
} from '@/components/ai/bartolo-chat';
import type { BartoloMessage, BartoloAction, ActionPreview } from '@/components/ai/bartolo-chat';

export function BartoloChat() {
  const pathname = usePathname();
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<BartoloMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [hasNewMessage, setHasNewMessage] = useState(false);
  const [actionPreview, setActionPreview] = useState<ActionPreview | null>(null);
  const [isExecutingAction, setIsExecutingAction] = useState(false);
  const [sessionId] = useState(() => BartoloService.generateSessionId());

  const currentModule = BartoloService.detectModule(pathname);

  const {
    greeting,
    sendMessage,
    isSending,
    lastResponse,
    submitFeedback,
    suggestions: moduleSuggestions,
  } = useBartoloChat(sessionId, currentModule);

  // Greeting inicial
  useEffect(() => {
    if (greeting && messages.length === 0) {
      setMessages([{
        id: 'greeting',
        role: 'assistant',
        content: greeting,
        timestamp: new Date(),
      }]);
    }
  }, [greeting, messages.length]);

  // Resposta do Bartolo
  useEffect(() => {
    if (lastResponse) {
      const resp = lastResponse as unknown as Record<string, unknown>;
      const assistantMessage: BartoloMessage = {
        id: resp.message_id as string,
        role: 'assistant',
        content: resp.response as string,
        contentHtml: resp.response_html as string | undefined,
        timestamp: new Date(),
        suggestions: (resp.suggestions as string[]) || [],
        actions: resp.actions as BartoloAction[] | undefined,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (resp.action_preview) {
        setActionPreview(resp.action_preview as ActionPreview);
      }
    }
  }, [lastResponse]);

  // Auto-scroll
  useEffect(() => {
    if (messagesEndRef.current && isOpen && !isMinimized) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen, isMinimized]);

  // Auto-focus input
  useEffect(() => {
    if (isOpen && !isMinimized && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen, isMinimized]);

  const toggleChat = useCallback(() => {
    setIsOpen((prev) => !prev);
    setIsMinimized(false);
    setHasNewMessage(false);
  }, []);

  const toggleMinimize = useCallback(() => {
    setIsMinimized((prev) => !prev);
  }, []);

  const handleSendMessage = useCallback(
    async (message: string) => {
      if (!message.trim() || isSending) return;

      setMessages((prev) => [...prev, {
        id: `user_${Date.now()}`,
        role: 'user',
        content: message.trim(),
        timestamp: new Date(),
      }]);
      setInputValue('');

      sendMessage({
        message: message.trim(),
        session_id: sessionId,
        module: currentModule,
        metadata: { pathname },
      });
    },
    [isSending, sendMessage, sessionId, currentModule, pathname]
  );

  const handleInputSubmit = useCallback(() => {
    handleSendMessage(inputValue);
  }, [handleSendMessage, inputValue]);

  const handleActionClick = (action: BartoloAction) => {
    if (action.type === 'navigate' && action.target) {
      window.location.href = action.target;
    }
  };

  const resetChat = useCallback(() => {
    setMessages([]);
    if (greeting) {
      setMessages([{
        id: 'greeting',
        role: 'assistant',
        content: greeting,
        timestamp: new Date(),
      }]);
    }
  }, [greeting]);

  const handleFeedback = (messageId: string, isPositive: boolean) => {
    submitFeedback({
      interaction_id: messageId,
      feedback_type: isPositive ? 'helpful' : 'not_helpful',
    });
  };

  const handleConfirmAction = useCallback(async () => {
    if (!actionPreview) return;

    setIsExecutingAction(true);
    try {
      const result = await BartoloService.confirmAction(
        Number(user?.id) || 0,
        actionPreview.action_id,
        true
      );

      const resp = result as unknown as Record<string, unknown>;
      setMessages((prev) => [...prev, {
        id: resp.message_id as string,
        role: 'assistant',
        content: resp.response as string,
        timestamp: new Date(),
      }]);
      setActionPreview(null);
    } catch {
      setMessages((prev) => [...prev, {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: 'Desculpe, ocorreu um erro ao executar a acao. Pode tentar novamente?',
        timestamp: new Date(),
      }]);
    } finally {
      setIsExecutingAction(false);
    }
  }, [actionPreview, user?.id]);

  const handleCancelAction = useCallback(async () => {
    if (!actionPreview) return;

    try {
      await BartoloService.confirmAction(
        Number(user?.id) || 0,
        actionPreview.action_id,
        false
      );
    } catch {
      // Silently ignore cancel errors
    }

    setActionPreview(null);
  }, [actionPreview, user?.id]);

  // Nao renderiza em paginas de login/auth
  if (pathname?.startsWith('/login') || pathname?.startsWith('/auth')) {
    return null;
  }

  return (
    <>
      {/* Botao Flutuante */}
      <button
        onClick={toggleChat}
        className={cn(
          'fixed bottom-6 right-6 z-50 group',
          'w-14 h-14 sm:w-16 sm:h-16 rounded-full',
          'bg-gradient-to-br from-brand-500 via-brand-600 to-brand-700',
          'hover:from-brand-400 hover:via-brand-500 hover:to-brand-600',
          'shadow-2xl shadow-brand-500/40',
          'hover:shadow-brand-400/50',
          'flex items-center justify-center',
          'transition-all duration-300 ease-out',
          'hover:scale-110 active:scale-95',
          'ring-4 ring-brand-400/20 hover:ring-brand-300/30',
          isOpen && 'scale-0 opacity-0 pointer-events-none'
        )}
        aria-label="Abrir chat com Bartolo"
      >
        <DachshundIcon className="w-9 h-9" animate />
        {hasNewMessage && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full animate-pulse border-2 border-white" />
        )}
      </button>

      {/* Janela do Chat */}
      <div
        className={cn(
          'fixed z-50',
          'transition-all duration-500 ease-out',
          'inset-0 sm:inset-auto sm:bottom-6 sm:right-6',
          isOpen
            ? 'opacity-100 translate-y-0 scale-100'
            : 'opacity-0 translate-y-8 scale-95 pointer-events-none',
          isMinimized ? 'sm:w-80' : 'sm:w-[26rem]'
        )}
      >
        <div
          className={cn(
            'bg-gradient-to-br from-slate-900/95 via-slate-900/98 to-slate-950/95',
            'backdrop-blur-xl shadow-2xl',
            'rounded-none sm:rounded-3xl',
            'border-0 sm:border sm:border-navy-700/40 sm:hover:border-brand-500/30',
            'transition-all duration-300',
            'overflow-hidden',
            'flex flex-col',
            isMinimized ? 'h-16' : 'h-full sm:h-[36rem]'
          )}
        >
          <ChatHeader
            isMinimized={isMinimized}
            onReset={resetChat}
            onToggleMinimize={toggleMinimize}
            onClose={toggleChat}
          />

          {!isMinimized && (
            <>
              <ChatMessages
                ref={messagesEndRef}
                messages={messages}
                isSending={isSending}
                onFeedback={handleFeedback}
                onActionClick={handleActionClick}
              />

              {messages.length === 0 && (
                <ChatSuggestions
                  suggestions={moduleSuggestions}
                  onSuggestionClick={handleSendMessage}
                />
              )}

              <ChatInput
                ref={inputRef}
                value={inputValue}
                isSending={isSending}
                onChange={setInputValue}
                onSubmit={handleInputSubmit}
              />
            </>
          )}
        </div>
      </div>

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

export default BartoloChat;
