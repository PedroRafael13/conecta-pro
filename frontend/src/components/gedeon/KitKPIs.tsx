'use client';

import type { CompletudeKit } from '@/types/kit-completude';
import { Card } from '@/components/ui/card';

interface KitKPIsProps {
  kits: CompletudeKit[];
}

export function KitKPIs({ kits }: KitKPIsProps) {
  const total = kits.length;
  const elegiveis = kits.filter((k) => k.tipo_servico !== 'administrativo');

  const pctMediaConfirmada =
    elegiveis.length > 0
      ? elegiveis.reduce((acc, k) => acc + k.metricas.pct_completude_confirmada, 0) /
        elegiveis.length
      : 0;

  const pctMediaTotal =
    elegiveis.length > 0
      ? elegiveis.reduce((acc, k) => acc + k.metricas.pct_completude_total, 0) / elegiveis.length
      : 0;

  const totalRevisao = kits.reduce(
    (acc, k) => acc + k.metricas.total_presente_pendente_revisao,
    0,
  );

  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
      <Card className="p-4">
        <div className="text-sm text-gray-600">Total condomínios</div>
        <div className="text-3xl font-bold text-[#0A2540]">{total}</div>
      </Card>
      <Card className="p-4">
        <div className="text-sm text-gray-600">Completude confirmada</div>
        <div className="text-3xl font-bold text-blue-600">{pctMediaConfirmada.toFixed(1)}%</div>
        <div className="text-xs text-gray-400 mt-1">média dos elegíveis</div>
      </Card>
      <Card className="p-4">
        <div className="text-sm text-gray-600">Completude total</div>
        <div className="text-3xl font-bold text-green-600">{pctMediaTotal.toFixed(1)}%</div>
        <div className="text-xs text-gray-400 mt-1">incluindo pendentes</div>
      </Card>
      <Card className="p-4">
        <div className="text-sm text-gray-600">Docs em revisão</div>
        <div className="text-3xl font-bold text-amber-600">{totalRevisao}</div>
      </Card>
    </div>
  );
}
