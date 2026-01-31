'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { usePathname } from 'next/navigation';
import {
  X,
  Send,
  Loader2,
  User,
  ThumbsUp,
  ThumbsDown,
  Minimize2,
  Maximize2,
  RotateCcw,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useBartoloChat } from '@/hooks/ai/useBartolo';
import { ActionConfirmationModal } from '@/components/ai/ActionConfirmationModal';

// Types
interface BartoloMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  contentHtml?: string;
  timestamp: Date;
  suggestions?: string[];
  actions?: BartoloAction[];
}

interface BartoloAction {
  type: 'navigate' | 'create' | 'edit' | 'delete' | 'export' | 'help';
  label: string;
  target?: string;
  data?: Record<string, unknown>;
}

interface ActionPreview {
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

// Componente SVG do Dachshund (Cachorro Salsicha)
function DachshundIcon({ className = 'w-6 h-6', animate = false }: { className?: string; animate?: boolean }) {
  return (
    <svg
      viewBox="0 0 64 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn(className, animate && 'group')}
    >
      {/* Corpo longo */}
      <ellipse
        cx="32"
        cy="24"
        rx="22"
        ry="10"
        fill="#D2691E"
        stroke="#8B4513"
        strokeWidth="1.5"
      />

      {/* Cabeca */}
      <ellipse
        cx="50"
        cy="22"
        rx="8"
        ry="7"
        fill="#D2691E"
        stroke="#8B4513"
        strokeWidth="1.5"
      />

      {/* Focinho */}
      <ellipse
        cx="56"
        cy="23"
        rx="4"
        ry="3.5"
        fill="#A0522D"
        stroke="#8B4513"
        strokeWidth="1"
      />

      {/* Nariz */}
      <circle cx="58" cy="23" r="1.5" fill="#000" />

      {/* Orelha esquerda */}
      <ellipse
        cx="48"
        cy="16"
        rx="3"
        ry="6"
        fill="#A0522D"
        stroke="#8B4513"
        strokeWidth="1"
        transform="rotate(-15 48 16)"
      />

      {/* Orelha direita */}
      <ellipse
        cx="52"
        cy="16"
        rx="3"
        ry="6"
        fill="#A0522D"
        stroke="#8B4513"
        strokeWidth="1"
        transform="rotate(15 52 16)"
      />

      {/* Olho */}
      <circle cx="52" cy="20" r="1.5" fill="#000" />

      {/* Pernas (4 pernas curtas) */}
      <rect x="18" y="32" width="2.5" height="8" rx="1.25" fill="#8B4513" />
      <rect x="26" y="32" width="2.5" height="8" rx="1.25" fill="#8B4513" />
      <rect x="38" y="32" width="2.5" height="8" rx="1.25" fill="#8B4513" />
      <rect x="46" y="32" width="2.5" height="8" rx="1.25" fill="#8B4513" />

      {/* Patinhas */}
      <ellipse cx="19.25" cy="41" rx="2" ry="1.5" fill="#A0522D" />
      <ellipse cx="27.25" cy="41" rx="2" ry="1.5" fill="#A0522D" />
      <ellipse cx="39.25" cy="41" rx="2" ry="1.5" fill="#A0522D" />
      <ellipse cx="47.25" cy="41" rx="2" ry="1.5" fill="#A0522D" />

      {/* Rabo (com animacao) */}
      <path
        d="M 10 20 Q 8 18 6 20 Q 4 22 5 24"
        stroke="#8B4513"
        strokeWidth="2.5"
        fill="none"
        strokeLinecap="round"
        className={cn(
          animate && 'origin-[10px_20px] group-hover:animate-[wag_0.5s_ease-in-out_infinite]'
        )}
      />
    </svg>
  );
}

export function BartoloChat() {
  const pathname = usePathname();
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

  // Detecta modulo atual
  const currentModule = BartoloService.detectModule(pathname);

  // Hook do Bartolo
  const {
    greeting,
    sendMessage,
    isSending,
    lastResponse,
    submitFeedback,
    suggestions: moduleSuggestions,
  } = useBartoloChat(sessionId, currentModule);

  // Adiciona greeting inicial
  useEffect(() => {
    if (greeting && messages.length === 0) {
      const greetingMessage: BartoloMessage = {
        id: 'greeting',
        role: 'assistant',
        content: greeting,
        timestamp: new Date(),
      };
      setMessages([greetingMessage]);
    }
  }, [greeting]);

  // Adiciona resposta do Bartolo quando recebe
  useEffect(() => {
    if (lastResponse) {
      const assistantMessage: BartoloMessage = {
        id: lastResponse.message_id,
        role: 'assistant',
        content: lastResponse.response,
        contentHtml: lastResponse.response_html,
        timestamp: new Date(),
        suggestions: (lastResponse.suggestions as string[]) || [],
        actions: lastResponse.actions as BartoloAction[] | undefined,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Verifica se há action_preview
      // @ts-ignore - action_preview ainda não está no tipo gerado
      if (lastResponse.action_preview) {
        // @ts-ignore
        setActionPreview(lastResponse.action_preview as ActionPreview);
      }
    }
  }, [lastResponse]);

  // Scroll para ultima mensagem
  useEffect(() => {
    if (messagesEndRef.current && isOpen && !isMinimized) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen, isMinimized]);

  // Focus no input quando abre
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

      const userMessage: BartoloMessage = {
        id: `user_${Date.now()}`,
        role: 'user',
        content: message.trim(),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSendMessage(inputValue);
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSendMessage(suggestion);
  };

  const handleActionClick = (action: BartoloAction) => {
    if (action.type === 'navigate' && action.target) {
      window.location.href = action.target;
    }
    // Outros tipos de acao podem ser implementados conforme necessario
  };

  const resetChat = useCallback(() => {
    setMessages([]);
    // Session ID não muda, apenas limpa mensagens
    if (greeting) {
      const greetingMessage: BartoloMessage = {
        id: 'greeting',
        role: 'assistant',
        content: greeting,
        timestamp: new Date(),
      };
      setMessages([greetingMessage]);
    }
  }, [greeting]);

  const handleFeedback = async (messageId: string, isPositive: boolean) => {
    submitFeedback({
      interaction_id: messageId,
      feedback_type: isPositive ? 'helpful' : 'not_helpful',
    });
  };

  // Handler para confirmar ação do Bartolo
  const handleConfirmAction = useCallback(async () => {
    if (!actionPreview) return;

    setIsExecutingAction(true);
    try {
      const userId = 1; // TODO: Obter userId do contexto de autenticacao

      const result = await BartoloService.confirmAction(
        userId,
        actionPreview.action_id,
        true
      );

      // Adiciona resultado da execução nas mensagens
      const resultMessage: BartoloMessage = {
        id: result.message_id,
        role: 'assistant',
        content: result.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, resultMessage]);
      setActionPreview(null);
    } catch (error) {
      console.error('Erro ao executar ação:', error);

      const errorMessage: BartoloMessage = {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: 'Desculpe, ocorreu um erro ao executar a ação. Pode tentar novamente?',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsExecutingAction(false);
    }
  }, [actionPreview]);

  // Handler para cancelar ação do Bartolo
  const handleCancelAction = useCallback(async () => {
    if (!actionPreview) return;

    try {
      const userId = 1; // TODO: Obter do contexto
      await BartoloService.confirmAction(
        userId,
        actionPreview.action_id,
        false
      );
    } catch (error) {
      console.error('Erro ao cancelar ação:', error);
    }

    setActionPreview(null);
  }, [actionPreview]);

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
          'w-14 h-14 rounded-full',
          'bg-gradient-to-br from-amber-600 to-amber-700',
          'hover:from-amber-500 hover:to-amber-600',
          'shadow-lg shadow-amber-600/25',
          'flex items-center justify-center',
          'transition-all duration-300 ease-out',
          'hover:scale-110 active:scale-95',
          isOpen && 'scale-0 opacity-0 pointer-events-none'
        )}
        aria-label="Abrir chat com Bartolo"
      >
        <DachshundIcon className="w-8 h-8" animate />
        {hasNewMessage && (
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full animate-pulse" />
        )}
      </button>

      {/* Janela do Chat */}
      <div
        className={cn(
          'fixed bottom-6 right-6 z-50',
          'transition-all duration-300 ease-out',
          isOpen
            ? 'opacity-100 translate-y-0'
            : 'opacity-0 translate-y-4 pointer-events-none',
          isMinimized ? 'w-72' : 'w-96'
        )}
      >
        <div
          className={cn(
            'bg-slate-900 rounded-2xl shadow-2xl',
            'border border-slate-700/50',
            'overflow-hidden',
            'flex flex-col',
            isMinimized ? 'h-14' : 'h-[32rem]'
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-amber-700 to-amber-600">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                <DachshundIcon className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">Bartolo</h3>
                {!isMinimized && (
                  <p className="text-xs text-amber-100/80">
                    Assistente Conecta PRO
                  </p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={resetChat}
                className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
                title="Reiniciar conversa"
              >
                <RotateCcw className="w-4 h-4 text-white/80" />
              </button>
              <button
                onClick={toggleMinimize}
                className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
                title={isMinimized ? 'Expandir' : 'Minimizar'}
              >
                {isMinimized ? (
                  <Maximize2 className="w-4 h-4 text-white/80" />
                ) : (
                  <Minimize2 className="w-4 h-4 text-white/80" />
                )}
              </button>
              <button
                onClick={toggleChat}
                className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
                title="Fechar"
              >
                <X className="w-4 h-4 text-white/80" />
              </button>
            </div>
          </div>

          {/* Corpo do Chat (escondido quando minimizado) */}
          {!isMinimized && (
            <>
              {/* Area de Mensagens */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center">
                    <div className="w-20 h-20 rounded-full bg-amber-500/10 flex items-center justify-center mb-4">
                      <DachshundIcon className="w-12 h-12" />
                    </div>
                    <h4 className="text-sm font-medium text-slate-200 mb-1">
                      Ola! Sou o Bartolo
                    </h4>
                    <p className="text-xs text-slate-400 max-w-[200px]">
                      Seu assistente IA do Conecta PRO. Como posso ajudar?
                    </p>
                  </div>
                ) : (
                  messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={cn(
                        'flex gap-2',
                        msg.role === 'user' ? 'justify-end' : 'justify-start'
                      )}
                    >
                      {msg.role === 'assistant' && (
                        <div className="w-7 h-7 rounded-full bg-amber-500/20 flex-shrink-0 flex items-center justify-center">
                          <DachshundIcon className="w-4 h-4" />
                        </div>
                      )}
                      <div
                        className={cn(
                          'max-w-[80%] rounded-2xl px-4 py-2.5',
                          msg.role === 'user'
                            ? 'bg-amber-600 text-white rounded-br-md'
                            : 'bg-slate-800 text-slate-200 rounded-bl-md'
                        )}
                      >
                        {msg.contentHtml ? (
                          <div
                            className="text-sm prose prose-invert prose-sm max-w-none"
                            dangerouslySetInnerHTML={{ __html: msg.contentHtml }}
                          />
                        ) : (
                          <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                        )}

                        {/* Acoes */}
                        {msg.actions && msg.actions.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1">
                            {msg.actions.map((action, idx) => (
                              <button
                                key={idx}
                                onClick={() => handleActionClick(action)}
                                className="text-xs px-2 py-1 rounded-full bg-amber-500/20 text-amber-400 hover:bg-amber-500/30 transition-colors"
                              >
                                {action.label}
                              </button>
                            ))}
                          </div>
                        )}

                        {/* Feedback (so para mensagens do assistente) */}
                        {msg.role === 'assistant' && (
                          <div className="mt-2 flex gap-1 opacity-0 hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => handleFeedback(msg.id, true)}
                              className="p-1 rounded hover:bg-slate-700/50"
                              title="Util"
                            >
                              <ThumbsUp className="w-3 h-3 text-slate-500" />
                            </button>
                            <button
                              onClick={() => handleFeedback(msg.id, false)}
                              className="p-1 rounded hover:bg-slate-700/50"
                              title="Nao ajudou"
                            >
                              <ThumbsDown className="w-3 h-3 text-slate-500" />
                            </button>
                          </div>
                        )}
                      </div>
                      {msg.role === 'user' && (
                        <div className="w-7 h-7 rounded-full bg-slate-700 flex-shrink-0 flex items-center justify-center">
                          <User className="w-4 h-4 text-slate-400" />
                        </div>
                      )}
                    </div>
                  ))
                )}

                {/* Indicador de digitando */}
                {isSending && (
                  <div className="flex gap-2 items-start">
                    <div className="w-7 h-7 rounded-full bg-amber-500/20 flex-shrink-0 flex items-center justify-center">
                      <DachshundIcon className="w-4 h-4" />
                    </div>
                    <div className="bg-slate-800 rounded-2xl rounded-bl-md px-4 py-3">
                      <div className="flex gap-1">
                        <span className="w-2 h-2 bg-amber-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
                        <span className="w-2 h-2 bg-amber-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
                        <span className="w-2 h-2 bg-amber-500 rounded-full animate-bounce" />
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Sugestoes Rapidas */}
              {messages.length === 0 && moduleSuggestions.length > 0 && (
                <div className="px-4 pb-2">
                  <p className="text-xs text-slate-500 mb-2">Sugestoes:</p>
                  <div className="flex flex-wrap gap-1.5">
                    {moduleSuggestions.slice(0, 4).map((suggestion, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="text-xs px-3 py-1.5 rounded-full bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-amber-400 transition-colors border border-slate-700/50"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Input */}
              <form onSubmit={handleSubmit} className="p-3 border-t border-slate-700/50">
                <div className="flex gap-2">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="Digite sua mensagem..."
                    disabled={isSending}
                    className={cn(
                      'flex-1 bg-slate-800 rounded-xl px-4 py-2.5',
                      'text-sm text-slate-200 placeholder:text-slate-500',
                      'border border-slate-700/50',
                      'focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500/50',
                      'disabled:opacity-50 disabled:cursor-not-allowed'
                    )}
                  />
                  <button
                    type="submit"
                    disabled={!inputValue.trim() || isSending}
                    className={cn(
                      'w-10 h-10 rounded-xl',
                      'bg-amber-600 hover:bg-amber-500',
                      'flex items-center justify-center',
                      'transition-colors',
                      'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-amber-600'
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
            </>
          )}
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

export default BartoloChat;
