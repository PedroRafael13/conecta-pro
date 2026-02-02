'use client';

import { X, Send, Loader2, User, ThumbsUp, ThumbsDown, Minimize2, Maximize2, RotateCcw } from 'lucide-react';
import { useState, useEffect, useRef, useCallback } from 'react';
import { usePathname } from 'next/navigation';
;
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
      const responseWithPreview = lastResponse as typeof lastResponse & { action_preview?: ActionPreview };
      if (responseWithPreview.action_preview) {
        setActionPreview(responseWithPreview.action_preview);
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
          'w-16 h-16 rounded-full',
          'bg-gradient-to-br from-amber-500 via-amber-600 to-orange-600',
          'hover:from-amber-400 hover:via-amber-500 hover:to-orange-500',
          'shadow-2xl shadow-amber-500/40',
          'hover:shadow-amber-400/50',
          'flex items-center justify-center',
          'transition-all duration-300 ease-out',
          'hover:scale-110 active:scale-95',
          'ring-4 ring-amber-400/20 hover:ring-amber-300/30',
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
          'fixed bottom-6 right-6 z-50',
          'transition-all duration-500 ease-out',
          isOpen
            ? 'opacity-100 translate-y-0 scale-100'
            : 'opacity-0 translate-y-8 scale-95 pointer-events-none',
          isMinimized ? 'w-80' : 'w-[26rem]'
        )}
      >
        <div
          className={cn(
            'bg-gradient-to-br from-slate-900/95 via-slate-900/98 to-slate-950/95',
            'backdrop-blur-xl rounded-3xl shadow-2xl',
            'border border-amber-500/20 hover:border-amber-400/30',
            'transition-all duration-300',
            'overflow-hidden',
            'flex flex-col',
            isMinimized ? 'h-16' : 'h-[36rem]'
          )}
        >
          {/* Header */}
          <div className="relative flex items-center justify-between px-5 py-4 bg-gradient-to-r from-amber-600 via-amber-500 to-orange-500 overflow-hidden">
            {/* Background pattern */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(255,255,255,0.1),transparent)] pointer-events-none" />

            <div className="flex items-center gap-3 relative z-10">
              <div className="w-10 h-10 rounded-full bg-white/25 backdrop-blur-sm flex items-center justify-center ring-2 ring-white/30 shadow-lg">
                <DachshundIcon className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-base font-bold text-white tracking-tight">Bartolo</h3>
                  <span className="w-2 h-2 rounded-full bg-green-400 shadow-lg shadow-green-400/50 animate-pulse" />
                </div>
                {!isMinimized && (
                  <p className="text-xs text-white/90 font-medium">
                    Assistente IA • Online
                  </p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-1.5 relative z-10">
              <button
                onClick={resetChat}
                className="p-2 rounded-xl hover:bg-white/20 active:bg-white/30 transition-all duration-200 group"
                title="Reiniciar conversa"
              >
                <RotateCcw className="w-4 h-4 text-white group-hover:rotate-180 transition-transform duration-500" />
              </button>
              <button
                onClick={toggleMinimize}
                className="p-2 rounded-xl hover:bg-white/20 active:bg-white/30 transition-all duration-200 group"
                title={isMinimized ? 'Expandir' : 'Minimizar'}
              >
                {isMinimized ? (
                  <Maximize2 className="w-4 h-4 text-white group-hover:scale-110 transition-transform" />
                ) : (
                  <Minimize2 className="w-4 h-4 text-white group-hover:scale-110 transition-transform" />
                )}
              </button>
              <button
                onClick={toggleChat}
                className="p-2 rounded-xl hover:bg-white/20 active:bg-white/30 transition-all duration-200 group"
                title="Fechar"
              >
                <X className="w-4 h-4 text-white group-hover:rotate-90 transition-transform duration-300" />
              </button>
            </div>
          </div>

          {/* Corpo do Chat (escondido quando minimizado) */}
          {!isMinimized && (
            <>
              {/* Area de Mensagens */}
              <div className="flex-1 overflow-y-auto p-5 space-y-4 scrollbar-thin scrollbar-thumb-amber-500/20 scrollbar-track-transparent">
                {messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center animate-in fade-in duration-500">
                    <div className="w-24 h-24 rounded-full bg-gradient-to-br from-amber-500/20 to-orange-500/10 flex items-center justify-center mb-5 ring-4 ring-amber-500/10 shadow-xl">
                      <DachshundIcon className="w-14 h-14 animate-in zoom-in duration-700" />
                    </div>
                    <h4 className="text-base font-bold text-slate-100 mb-2 bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">
                      Olá! Sou o Bartolo
                    </h4>
                    <p className="text-sm text-slate-400 max-w-[240px] leading-relaxed">
                      Seu assistente IA do Conecta PRO. Como posso ajudar você hoje?
                    </p>
                  </div>
                ) : (
                  messages.map((msg, idx) => (
                    <div
                      key={msg.id}
                      className={cn(
                        'flex gap-2.5 animate-in fade-in slide-in-from-bottom-4',
                        msg.role === 'user' ? 'justify-end' : 'justify-start'
                      )}
                      style={{ animationDelay: `${idx * 50}ms` }}
                    >
                      {msg.role === 'assistant' && (
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-500/30 to-orange-500/20 flex-shrink-0 flex items-center justify-center ring-2 ring-amber-500/20 shadow-lg">
                          <DachshundIcon className="w-5 h-5" />
                        </div>
                      )}
                      <div
                        className={cn(
                          'max-w-[82%] rounded-2xl px-4 py-3 shadow-lg',
                          'transition-all duration-200 hover:shadow-xl',
                          msg.role === 'user'
                            ? 'bg-gradient-to-br from-amber-500 to-amber-600 text-white rounded-br-sm'
                            : 'bg-slate-800/80 backdrop-blur-sm text-slate-100 rounded-bl-sm border border-slate-700/50'
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
                          <div className="mt-3 flex flex-wrap gap-2">
                            {msg.actions.map((action, idx) => (
                              <button
                                key={idx}
                                onClick={() => handleActionClick(action)}
                                className="text-xs px-3 py-1.5 rounded-full bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-amber-300 hover:from-amber-500/30 hover:to-orange-500/30 hover:text-amber-200 transition-all duration-200 border border-amber-500/30 hover:border-amber-400/50 shadow-sm hover:shadow-amber-500/20 font-medium"
                              >
                                {action.label}
                              </button>
                            ))}
                          </div>
                        )}

                        {/* Feedback (so para mensagens do assistente) */}
                        {msg.role === 'assistant' && (
                          <div className="mt-2.5 flex gap-1.5 opacity-60 hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => handleFeedback(msg.id, true)}
                              className="p-1.5 rounded-lg hover:bg-green-500/20 active:bg-green-500/30 transition-all group"
                              title="Útil"
                            >
                              <ThumbsUp className="w-3.5 h-3.5 text-slate-500 group-hover:text-green-400 transition-colors" />
                            </button>
                            <button
                              onClick={() => handleFeedback(msg.id, false)}
                              className="p-1.5 rounded-lg hover:bg-red-500/20 active:bg-red-500/30 transition-all group"
                              title="Não ajudou"
                            >
                              <ThumbsDown className="w-3.5 h-3.5 text-slate-500 group-hover:text-red-400 transition-colors" />
                            </button>
                          </div>
                        )}
                      </div>
                      {msg.role === 'user' && (
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 flex-shrink-0 flex items-center justify-center ring-2 ring-slate-600/50 shadow-lg">
                          <User className="w-4 h-4 text-slate-300" />
                        </div>
                      )}
                    </div>
                  ))
                )}

                {/* Indicador de digitando */}
                {isSending && (
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
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Sugestoes Rapidas */}
              {messages.length === 0 && moduleSuggestions.length > 0 && (
                <div className="px-5 pb-3 animate-in fade-in slide-in-from-bottom-4 delay-300">
                  <p className="text-xs font-semibold text-amber-400/80 mb-2.5 flex items-center gap-2">
                    <span className="w-1 h-1 rounded-full bg-amber-400 animate-pulse" />
                    Sugestões rápidas
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {moduleSuggestions.slice(0, 4).map((suggestion, idx) => (
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
              <form onSubmit={handleSubmit} className="p-4 border-t border-slate-700/30 bg-slate-900/50 backdrop-blur-sm">
                <div className="flex gap-2.5">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
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
                    disabled={!inputValue.trim() || isSending}
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
