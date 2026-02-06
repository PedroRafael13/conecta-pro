'use client';

import { useState } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { TenantResponse } from '@/types/generated/config/conectaPROCONFIGModuleAPI.schemas';

interface TenantDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  tenant: TenantResponse | null;
  onUpdatePlan: (plan: any) => Promise<void>;
  onUpdateAddress: (address: any) => Promise<void>;
  onEnableFeature: (feature: string) => Promise<void>;
  onDisableFeature: (feature: string) => Promise<void>;
  isLoading?: boolean;
}

const AVAILABLE_FEATURES = [
  'crm', 'services', 'operacional', 'campo', 'financial',
  'government', 'ged', 'equipment', 'integrations', 'reports',
];

export function TenantDetailModal({
  isOpen,
  onClose,
  tenant,
  onUpdatePlan,
  onUpdateAddress,
  onEnableFeature,
  onDisableFeature,
  isLoading,
}: TenantDetailModalProps) {
  const [planForm, setPlanForm] = useState({
    plan: tenant?.plan || 'free',
    max_users: tenant?.max_users || 10,
    max_units: tenant?.max_units || 5,
  });
  const [addressForm, setAddressForm] = useState({
    logradouro: '',
    numero: '',
    complemento: '',
    bairro: '',
    cidade: '',
    estado: '',
    cep: '',
  });

  if (!tenant) return null;

  const enabledFeatures = tenant.features_enabled || [];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={tenant.nome}
      description={`${tenant.codigo} - ${tenant.email}`}
      size="xl"
    >
      <Tabs defaultValue="geral" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="geral">Dados Gerais</TabsTrigger>
          <TabsTrigger value="plano">Plano / Limites</TabsTrigger>
          <TabsTrigger value="features">Features</TabsTrigger>
        </TabsList>

        <TabsContent value="geral" className="space-y-4 mt-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-muted-foreground text-xs">Codigo</Label>
              <p className="font-mono text-sm">{tenant.codigo}</p>
            </div>
            <div>
              <Label className="text-muted-foreground text-xs">Status</Label>
              <div className="mt-1">
                <Badge className={
                  tenant.status === 'active' ? 'bg-green-100 text-green-800' :
                  tenant.status === 'trial' ? 'bg-blue-100 text-blue-800' :
                  tenant.status === 'suspended' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }>
                  {tenant.status}
                </Badge>
              </div>
            </div>
            <div>
              <Label className="text-muted-foreground text-xs">Email</Label>
              <p className="text-sm">{tenant.email}</p>
            </div>
            <div>
              <Label className="text-muted-foreground text-xs">CNPJ</Label>
              <p className="text-sm">{tenant.cnpj || '-'}</p>
            </div>
            <div>
              <Label className="text-muted-foreground text-xs">Telefone</Label>
              <p className="text-sm">{tenant.telefone || '-'}</p>
            </div>
            <div>
              <Label className="text-muted-foreground text-xs">Tipo</Label>
              <p className="text-sm">{tenant.tenant_type || '-'}</p>
            </div>
            <div>
              <Label className="text-muted-foreground text-xs">Criado em</Label>
              <p className="text-sm">{new Date(tenant.created_at).toLocaleDateString('pt-BR')}</p>
            </div>
            <div>
              <Label className="text-muted-foreground text-xs">Usuarios</Label>
              <p className="text-sm">{tenant.current_users ?? 0} / {tenant.max_users}</p>
            </div>
          </div>

          {/* Address */}
          <div className="border-t pt-4 mt-4">
            <h4 className="font-medium mb-3">Endereco</h4>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-1">
                <Label htmlFor="logradouro" className="text-xs">Logradouro</Label>
                <Input
                  id="logradouro"
                  value={addressForm.logradouro}
                  onChange={(e) => setAddressForm({ ...addressForm, logradouro: e.target.value })}
                  placeholder="Rua..."
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="grid gap-1">
                  <Label htmlFor="numero" className="text-xs">Numero</Label>
                  <Input
                    id="numero"
                    value={addressForm.numero}
                    onChange={(e) => setAddressForm({ ...addressForm, numero: e.target.value })}
                  />
                </div>
                <div className="grid gap-1">
                  <Label htmlFor="cep" className="text-xs">CEP</Label>
                  <Input
                    id="cep"
                    value={addressForm.cep}
                    onChange={(e) => setAddressForm({ ...addressForm, cep: e.target.value })}
                  />
                </div>
              </div>
              <div className="grid gap-1">
                <Label htmlFor="cidade" className="text-xs">Cidade</Label>
                <Input
                  id="cidade"
                  value={addressForm.cidade}
                  onChange={(e) => setAddressForm({ ...addressForm, cidade: e.target.value })}
                />
              </div>
              <div className="grid gap-1">
                <Label htmlFor="estado" className="text-xs">Estado</Label>
                <Input
                  id="estado"
                  value={addressForm.estado}
                  onChange={(e) => setAddressForm({ ...addressForm, estado: e.target.value })}
                />
              </div>
            </div>
            <div className="flex justify-end mt-3">
              <Button
                size="sm"
                onClick={() => onUpdateAddress(addressForm)}
                disabled={isLoading}
              >
                {isLoading ? 'Salvando...' : 'Salvar Endereco'}
              </Button>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="plano" className="space-y-4 mt-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="grid gap-2">
              <Label>Plano</Label>
              <Select
                value={planForm.plan}
                onValueChange={(v) => setPlanForm({ ...planForm, plan: v })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="free">Free</SelectItem>
                  <SelectItem value="starter">Starter</SelectItem>
                  <SelectItem value="pro">Pro</SelectItem>
                  <SelectItem value="enterprise">Enterprise</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="plan_max_users">Max Usuarios</Label>
              <Input
                id="plan_max_users"
                type="number"
                value={planForm.max_users}
                onChange={(e) => setPlanForm({ ...planForm, max_users: Number(e.target.value) })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="plan_max_units">Max Unidades</Label>
              <Input
                id="plan_max_units"
                type="number"
                value={planForm.max_units}
                onChange={(e) => setPlanForm({ ...planForm, max_units: Number(e.target.value) })}
              />
            </div>
          </div>
          <div className="flex justify-end">
            <Button
              onClick={() => onUpdatePlan(planForm)}
              disabled={isLoading}
            >
              {isLoading ? 'Salvando...' : 'Atualizar Plano'}
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="features" className="space-y-3 mt-4">
          <p className="text-sm text-muted-foreground mb-4">
            Habilite ou desabilite modulos para este tenant.
          </p>
          {AVAILABLE_FEATURES.map((feature) => {
            const enabled = enabledFeatures.includes(feature);
            return (
              <div
                key={feature}
                className="flex items-center justify-between py-2 border-b last:border-0"
              >
                <div>
                  <p className="text-sm font-medium capitalize">{feature}</p>
                </div>
                <Switch
                  checked={enabled}
                  onCheckedChange={(checked) => {
                    if (checked) {
                      onEnableFeature(feature);
                    } else {
                      onDisableFeature(feature);
                    }
                  }}
                  disabled={isLoading}
                />
              </div>
            );
          })}
        </TabsContent>
      </Tabs>
    </Modal>
  );
}
