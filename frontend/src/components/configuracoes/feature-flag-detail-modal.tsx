'use client';

import { useState } from 'react';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import type { FeatureFlagResponse } from '@/types/generated/config/conectaPROCONFIGModuleAPI.schemas';
import { getStatusLabel } from '@/services/config/feature-flags';

interface FeatureFlagDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  flag: FeatureFlagResponse | null;
  onSetPercentage: (percentage: number) => Promise<void>;
  onSetGradualRollout: (rollout: any) => Promise<void>;
  onToggleTenant: (tenantId: string, enabled: boolean) => Promise<void>;
  isLoading?: boolean;
}

export function FeatureFlagDetailModal({
  isOpen,
  onClose,
  flag,
  onSetPercentage,
  onSetGradualRollout,
  onToggleTenant,
  isLoading,
}: FeatureFlagDetailModalProps) {
  const [percentage, setPercentage] = useState(flag?.rollout_percentage || 0);
  const [gradualForm, setGradualForm] = useState({
    start_percentage: 0,
    end_percentage: 100,
    start_date: '',
    end_date: '',
  });
  const [tenantId, setTenantId] = useState('');

  if (!flag) return null;

  const tenantOverrides = flag.tenant_overrides || {};

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={flag.nome}
      description={`${flag.codigo} - ${getStatusLabel(flag)}`}
      size="xl"
    >
      <Tabs defaultValue="geral" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="geral">Geral</TabsTrigger>
          <TabsTrigger value="rollout">Rollout</TabsTrigger>
          <TabsTrigger value="tenants">Tenants</TabsTrigger>
        </TabsList>

        <TabsContent value="geral" className="space-y-4 mt-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-muted-foreground text-xs">Codigo</Label>
              <p className="font-mono text-sm">{flag.codigo}</p>
            </div>
            <div>
              <Label className="text-muted-foreground text-xs">Status</Label>
              <div className="mt-1">
                <Badge className={flag.ativo ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                  {flag.ativo ? 'Habilitada' : 'Desabilitada'}
                </Badge>
              </div>
            </div>
            <div>
              <Label className="text-muted-foreground text-xs">Tipo</Label>
              <p className="text-sm capitalize">{flag.flag_type}</p>
            </div>
            <div>
              <Label className="text-muted-foreground text-xs">Categoria</Label>
              <p className="text-sm capitalize">{flag.category || '-'}</p>
            </div>
            <div>
              <Label className="text-muted-foreground text-xs">Time</Label>
              <p className="text-sm">{flag.owner_team || '-'}</p>
            </div>
            <div>
              <Label className="text-muted-foreground text-xs">Rollout</Label>
              <p className="text-sm">{flag.rollout_percentage ?? 0}%</p>
            </div>
          </div>
          {flag.descricao && (
            <div>
              <Label className="text-muted-foreground text-xs">Descricao</Label>
              <p className="text-sm mt-1">{flag.descricao}</p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="rollout" className="space-y-6 mt-4">
          {/* Percentage */}
          <div className="space-y-3">
            <h4 className="font-medium">Percentual de Rollout</h4>
            <div className="flex items-center gap-4">
              <Input
                type="number"
                min={0}
                max={100}
                value={percentage}
                onChange={(e) => setPercentage(Number(e.target.value))}
                className="w-24"
              />
              <span className="text-sm text-muted-foreground">%</span>
              <Progress value={percentage} className="flex-1" />
            </div>
            <Button
              size="sm"
              onClick={() => onSetPercentage(percentage)}
              disabled={isLoading}
            >
              {isLoading ? 'Salvando...' : 'Aplicar Percentual'}
            </Button>
          </div>

          {/* Gradual Rollout */}
          <div className="space-y-3 border-t pt-4">
            <h4 className="font-medium">Rollout Gradual</h4>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label className="text-xs">% Inicial</Label>
                <Input
                  type="number"
                  min={0}
                  max={100}
                  value={gradualForm.start_percentage}
                  onChange={(e) => setGradualForm({ ...gradualForm, start_percentage: Number(e.target.value) })}
                />
              </div>
              <div className="grid gap-2">
                <Label className="text-xs">% Final</Label>
                <Input
                  type="number"
                  min={0}
                  max={100}
                  value={gradualForm.end_percentage}
                  onChange={(e) => setGradualForm({ ...gradualForm, end_percentage: Number(e.target.value) })}
                />
              </div>
              <div className="grid gap-2">
                <Label className="text-xs">Data Inicio</Label>
                <Input
                  type="date"
                  value={gradualForm.start_date}
                  onChange={(e) => setGradualForm({ ...gradualForm, start_date: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label className="text-xs">Data Fim</Label>
                <Input
                  type="date"
                  value={gradualForm.end_date}
                  onChange={(e) => setGradualForm({ ...gradualForm, end_date: e.target.value })}
                />
              </div>
            </div>
            <Button
              size="sm"
              onClick={() => onSetGradualRollout(gradualForm)}
              disabled={isLoading}
            >
              {isLoading ? 'Salvando...' : 'Configurar Rollout Gradual'}
            </Button>
          </div>

          {/* Current Gradual Rollout Info */}
          {flag.gradual_rollout && (
            <div className="border-t pt-4">
              <h4 className="font-medium mb-2">Rollout Atual</h4>
              <div className="text-sm space-y-1 text-muted-foreground">
                <p>De {flag.gradual_rollout.start_percentage}% ate {flag.gradual_rollout.end_percentage}%</p>
                <p>Inicio: {flag.gradual_rollout.start_date} - Fim: {flag.gradual_rollout.end_date}</p>
              </div>
            </div>
          )}
        </TabsContent>

        <TabsContent value="tenants" className="space-y-4 mt-4">
          <div className="flex gap-2">
            <Input
              placeholder="ID do tenant..."
              value={tenantId}
              onChange={(e) => setTenantId(e.target.value)}
              className="flex-1"
            />
            <Button
              size="sm"
              onClick={() => {
                if (tenantId.trim()) {
                  onToggleTenant(tenantId.trim(), true);
                  setTenantId('');
                }
              }}
              disabled={isLoading || !tenantId.trim()}
            >
              Habilitar
            </Button>
          </div>

          {Object.keys(tenantOverrides).length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-6">
              Nenhum override de tenant configurado
            </p>
          ) : (
            <div className="space-y-2">
              {Object.entries(tenantOverrides).map(([tid, enabled]) => (
                <div key={tid} className="flex items-center justify-between py-2 border-b last:border-0">
                  <span className="text-sm font-mono">{tid}</span>
                  <Switch
                    checked={enabled}
                    onCheckedChange={(checked) => onToggleTenant(tid, checked)}
                    disabled={isLoading}
                  />
                </div>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </Modal>
  );
}
