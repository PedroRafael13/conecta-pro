'use client';

import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import type { NotificationTemplateResponse } from '@/types/generated/config/conectaPROCONFIGModuleAPI.schemas';
import { extractTemplateVariables } from '@/services/config/notification-templates';

interface TemplatePreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  template: NotificationTemplateResponse | null;
  onRender: (variables: Record<string, unknown>) => Promise<Record<string, unknown>>;
  isLoading?: boolean;
}

export function TemplatePreviewModal({
  isOpen,
  onClose,
  template,
  onRender,
  isLoading,
}: TemplatePreviewModalProps) {
  const [variables, setVariables] = useState<Record<string, string>>({});
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    if (template) {
      // Extract variables from all template content
      const allContent = [
        template.email_subject,
        template.body_html,
        template.body_text,
        template.sms_body,
        template.push_title,
        template.push_body,
        template.in_app_title,
        template.in_app_body,
      ].filter(Boolean).join(' ');

      const vars = extractTemplateVariables(allContent);
      const initial: Record<string, string> = {};
      vars.forEach((v) => { initial[v] = ''; });
      setVariables(initial);
      setResult(null);
    }
  }, [template, isOpen]);

  if (!template) return null;

  const variableKeys = Object.keys(variables);

  const handleRender = async () => {
    const rendered = await onRender(variables);
    setResult(rendered);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Preview do Template"
      description={`${template.nome} (${template.channel})`}
      size="xl"
    >
      <div className="grid gap-4">
        {/* Variables */}
        {variableKeys.length > 0 ? (
          <div className="space-y-3">
            <Label className="font-medium">Variaveis</Label>
            <div className="grid grid-cols-2 gap-3">
              {variableKeys.map((key) => (
                <div key={key} className="grid gap-1">
                  <Label className="text-xs text-muted-foreground font-mono">{`{{${key}}}`}</Label>
                  <Input
                    value={variables[key]}
                    onChange={(e) => setVariables({ ...variables, [key]: e.target.value })}
                    placeholder={`Valor para ${key}`}
                  />
                </div>
              ))}
            </div>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">Nenhuma variavel encontrada no template.</p>
        )}

        <Button onClick={handleRender} disabled={isLoading}>
          {isLoading ? 'Renderizando...' : 'Renderizar'}
        </Button>

        {/* Result */}
        {result && (
          <div className="border rounded-lg p-4 space-y-3">
            <div className="flex items-center gap-2">
              <Badge>{template.channel}</Badge>
              <span className="text-sm font-medium">Resultado</span>
            </div>
            {'subject' in result && result.subject ? (
              <div>
                <Label className="text-xs text-muted-foreground">Assunto</Label>
                <p className="text-sm font-medium">{String(result.subject)}</p>
              </div>
            ) : null}
            {'title' in result && result.title ? (
              <div>
                <Label className="text-xs text-muted-foreground">Titulo</Label>
                <p className="text-sm font-medium">{String(result.title)}</p>
              </div>
            ) : null}
            {'body_html' in result && result.body_html ? (
              <div>
                <Label className="text-xs text-muted-foreground">HTML</Label>
                <div
                  className="border rounded p-3 bg-white text-sm mt-1 max-h-[300px] overflow-auto"
                  dangerouslySetInnerHTML={{ __html: String(result.body_html) }}
                />
              </div>
            ) : null}
            {'body_text' in result && result.body_text ? (
              <div>
                <Label className="text-xs text-muted-foreground">Texto</Label>
                <pre className="text-sm mt-1 whitespace-pre-wrap bg-muted p-3 rounded">{String(result.body_text)}</pre>
              </div>
            ) : null}
            {'body' in result && result.body ? (
              <div>
                <Label className="text-xs text-muted-foreground">Mensagem</Label>
                <p className="text-sm mt-1">{String(result.body)}</p>
              </div>
            ) : null}
          </div>
        )}
      </div>
    </Modal>
  );
}
