'use client';

/**
 * Bartolo Chat Widget - Assistente IA Conversacional
 * Widget flutuante que pode ser aberto em qualquer página
 */

import { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, ThumbsUp, ThumbsDown, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { useBartoloChat } from '@/hooks/ai/useBartolo';
import { BartoloService } from '@/services/ai/bartolo.service';
import { toast } from 'sonner';
import { ActionConfirmationModal, type ActionPreview } from './ActionConfirmationModal';

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
      console.log('[BARTOLO DEBUG] lastResponse:', lastResponse);

      // Verifica se há action_preview (ação detectada)
      // @ts-ignore - action_preview ainda não está no tipo gerado
      console.log('[BARTOLO DEBUG] action_preview:', lastResponse.action_preview);

      // @ts-ignore - action_preview ainda não está no tipo gerado
      if (lastResponse.action_preview) {
        console.log('[BARTOLO DEBUG] ACTION PREVIEW DETECTADO! Setando estado...');
        // @ts-ignore
        setActionPreview(lastResponse.action_preview as ActionPreview);
        console.log('[BARTOLO DEBUG] Estado actionPreview setado');
      } else {
        console.log('[BARTOLO DEBUG] Nenhum action_preview na resposta');
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

  // DEBUG: Botão de teste para forçar modal
  const handleTestModal = () => {
    console.log('[BARTOLO TEST] Forçando modal de teste');
    const mockPreview: ActionPreview = {
      action_id: 'test-' + Date.now(),
      action_type: 'create_scale',
      title: 'TESTE - Criar Escala',
      description: 'Este é um teste do modal de confirmação',
      affected_entities: [{ type: 'post', id: 'test', name: 'Posto Teste' }],
      changes_summary: ['Teste 1', 'Teste 2'],
      warnings: [],
      required_permission: 'scales:create',
      user_has_permission: true,
      parameters: {},
      can_be_undone: true,
      requires_confirmation: true,
    };
    setActionPreview(mockPreview);
    console.log('[BARTOLO TEST] actionPreview setado para:', mockPreview);
  };

  const handleFeedback = (messageId: string, isPositive: boolean) => {
    submitFeedback({
      interaction_id: messageId,
      feedback_type: isPositive ? 'helpful' : 'not_helpful',
    });

    toast.success(
      isPositive
        ? 'Obrigado pelo feedback positivo!'
        : 'Vamos melhorar! Obrigado pelo feedback.'
    );
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
      <Button
        size="lg"
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg"
        onClick={() => setIsOpen(true)}
      >
        <MessageSquare className="h-6 w-6" />
      </Button>
    );
  }

  return (
    <>
    <Card className="fixed bottom-6 right-6 flex h-[600px] w-[400px] flex-col shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b bg-primary p-4 text-primary-foreground">
        <div className="flex items-center gap-3">
          <Avatar className="h-10 w-10 border-2 border-white">
            <AvatarFallback className="bg-primary-foreground text-primary">
              B
            </AvatarFallback>
          </Avatar>
          <div>
            <h3 className="font-semibold">Bartolo</h3>
            <p className="text-xs opacity-90">Assistente Inteligente</p>
          </div>
        </div>
        {/* DEBUG: Botão de teste */}
        <Button
          variant="ghost"
          size="sm"
          className="text-primary-foreground hover:bg-primary-foreground/20 text-xs mr-2"
          onClick={handleTestModal}
        >
          🧪 Test
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="text-primary-foreground hover:bg-primary-foreground/20"
          onClick={() => setIsOpen(false)}
        >
          <X className="h-5 w-5" />
        </Button>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="space-y-4">
          {isLoadingGreeting && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Bartolo está se preparando...</span>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${
                message.role === 'user' ? 'flex-row-reverse' : ''
              }`}
            >
              <Avatar className="h-8 w-8">
                <AvatarFallback
                  className={
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }
                >
                  {message.role === 'user' ? 'V' : 'B'}
                </AvatarFallback>
              </Avatar>

              <div
                className={`flex max-w-[80%] flex-col gap-2 ${
                  message.role === 'user' ? 'items-end' : ''
                }`}
              >
                <div
                  className={`rounded-lg px-4 py-2 ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>

                {/* Data Results */}
                {message.data_results && (
                  <div className="w-full rounded-lg border bg-card p-3 text-xs">
                    <div className="font-semibold mb-1">
                      📊 {message.data_results.entity}
                    </div>
                    <div className="text-muted-foreground">
                      {message.data_results.total_count} registros encontrados
                    </div>
                  </div>
                )}

                {/* Suggestions from message */}
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {message.suggestions.map((sug, idx) => (
                      <Badge
                        key={idx}
                        variant="outline"
                        className="cursor-pointer text-xs"
                        onClick={() => handleSuggestionClick(sug)}
                      >
                        {sug}
                      </Badge>
                    ))}
                  </div>
                )}

                {/* Feedback buttons */}
                {message.role === 'assistant' && message.id !== 'greeting' && (
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6"
                      onClick={() => handleFeedback(message.id, true)}
                    >
                      <ThumbsUp className="h-3 w-3" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6"
                      onClick={() => handleFeedback(message.id, false)}
                    >
                      <ThumbsDown className="h-3 w-3" />
                    </Button>
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
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Bartolo está pensando...</span>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Suggestions */}
      {messages.length <= 1 && suggestions.length > 0 && (
        <div className="border-t p-3">
          <p className="mb-2 text-xs font-medium text-muted-foreground">
            Sugestões:
          </p>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion, idx) => (
              <Badge
                key={idx}
                variant="secondary"
                className="cursor-pointer text-xs"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="border-t p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex gap-2"
        >
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Digite sua mensagem..."
            disabled={isSending}
            className="flex-1"
          />
          <Button type="submit" size="icon" disabled={isSending || !input.trim()}>
            {isSending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>
      </div>

      {/* DEBUG: Indicador de estado */}
      <div className="absolute top-2 left-2 text-xs bg-yellow-400 text-black px-1 rounded">
        {actionPreview ? '🔴 MODAL ON' : '⚪ MODAL OFF'}
      </div>
    </Card>

    {/* Modal de confirmação de ação - FORA do Card para evitar z-index issues */}
    {actionPreview && (
      <>
        {console.log('[BARTOLO DEBUG] RENDERIZANDO MODAL! actionPreview:', actionPreview)}
        <ActionConfirmationModal
          preview={actionPreview}
          onConfirm={handleConfirmAction}
          onCancel={handleCancelAction}
          isExecuting={isExecutingAction}
        />
      </>
    )}
    </>
  );
}
