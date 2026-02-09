'use client';

/**
 * Modal de Confirmação de Ação do Bartolo
 * Exibe preview da ação e solicita confirmação do usuário
 */

import { AlertTriangle, CheckCircle2, Info, Shield } from 'lucide-react';
import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
;
import { Alert, AlertDescription } from '@/components/ui/alert';

export interface ActionPreview {
  action_id: string;
  action_type: string;
  title: string;
  description: string;
  affected_entities: Array<{
    type: string;
    id: string;
    name?: string;
    code?: string;
  }>;
  changes_summary: string[];
  warnings: string[];
  required_permission: string;
  user_has_permission: boolean;
  parameters: Record<string, any>;
  can_be_undone: boolean;
  requires_confirmation: boolean;
}

interface ActionConfirmationModalProps {
  preview: ActionPreview;
  onConfirm: () => void;
  onCancel: () => void;
  isExecuting?: boolean;
}

export function ActionConfirmationModal({
  preview,
  onConfirm,
  onCancel,
  isExecuting = false,
}: ActionConfirmationModalProps) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <Dialog open onOpenChange={onCancel}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-blue-500" />
            <DialogTitle>{preview.title}</DialogTitle>
          </div>
          <DialogDescription>{preview.description}</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Resumo das mudanças */}
          {preview.changes_summary.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
                <Info className="h-4 w-4" />
                O que será feito:
              </h4>
              <ul className="space-y-1">
                {preview.changes_summary.map((change, index) => (
                  <li key={index} className="text-sm text-muted-foreground pl-6">
                    • {change}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Avisos */}
          {preview.warnings.length > 0 && (
            <Alert variant="default" className="border-yellow-500/50 bg-yellow-50 dark:bg-yellow-950">
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
              <AlertDescription>
                <div className="space-y-1">
                  {preview.warnings.map((warning, index) => (
                    <div key={index} className="text-sm">
                      {warning}
                    </div>
                  ))}
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* Falta de permissão */}
          {!preview.user_has_permission && (
            <Alert variant="destructive">
              <Shield className="h-4 w-4" />
              <AlertDescription>
                <div className="font-semibold mb-1">Permissão Necessária</div>
                <div className="text-sm">
                  Você não tem permissão para executar esta ação.
                  <br />
                  Permissão requerida: <code className="text-xs">{preview.required_permission}</code>
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* Informação sobre reversão */}
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            {preview.can_be_undone ? (
              <Badge variant="outline" className="text-green-600 border-green-600">
                ✓ Pode ser desfeita
              </Badge>
            ) : (
              <Badge variant="outline" className="text-orange-600 border-orange-600">
                ⚠ Não pode ser desfeita
              </Badge>
            )}
          </div>

          {/* Detalhes técnicos (colapsável) */}
          {showDetails && (
            <div className="border rounded-lg p-3 bg-muted/50">
              <h4 className="text-xs font-semibold mb-2">Detalhes Técnicos</h4>
              <div className="space-y-2 text-xs text-muted-foreground">
                <div>
                  <span className="font-medium">Action ID:</span>{' '}
                  <code className="text-xs">{preview.action_id}</code>
                </div>
                <div>
                  <span className="font-medium">Tipo:</span>{' '}
                  <code className="text-xs">{preview.action_type}</code>
                </div>
                {preview.affected_entities.length > 0 && (
                  <div>
                    <span className="font-medium">Entidades afetadas:</span>
                    <ul className="mt-1 space-y-1">
                      {preview.affected_entities.map((entity, index) => (
                        <li key={index}>
                          • {entity.type}: {entity.name || entity.code || entity.id}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="flex flex-col sm:flex-row gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowDetails(!showDetails)}
            className="text-xs"
          >
            {showDetails ? 'Ocultar' : 'Ver'} detalhes técnicos
          </Button>
          <div className="flex-1" />
          <Button
            variant="outline"
            onClick={onCancel}
            disabled={isExecuting}
          >
            Cancelar
          </Button>
          <Button
            onClick={onConfirm}
            disabled={!preview.user_has_permission || isExecuting}
          >
            {isExecuting ? (
              <>
                <span className="animate-spin mr-2">⏳</span>
                Executando...
              </>
            ) : (
              'Confirmar Ação'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
