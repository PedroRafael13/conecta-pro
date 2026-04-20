'use client';

import type { CompletudeKit, TipoServico } from '@/types/kit-completude';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

interface KitCardProps {
  kit: CompletudeKit;
  onClick: () => void;
}

function getCardClasses(pct: number, tipo: TipoServico): string {
  if (tipo === 'administrativo') return 'border-gray-500 bg-gray-50';
  if (pct >= 100) return 'border-green-600 bg-green-50';
  if (pct >= 80) return 'border-blue-600 bg-blue-50';
  if (pct >= 50) return 'border-amber-500 bg-amber-50';
  return 'border-red-600 bg-red-50';
}

const TIPO_LABELS: Record<TipoServico, string> = {
  kit_mensal: 'Kit Mensal',
  portaria_remota: 'Port. Remota',
  portaria_autonoma: 'Port. Autônoma',
  manutencao_cftv: 'Manutenção CFTV',
  administrativo: 'Administrativo',
};

export function KitCard({ kit, onClick }: KitCardProps) {
  const { condominio_nome, tipo_servico, metricas } = kit;
  const isAdmin = tipo_servico === 'administrativo';
  const pct = metricas.pct_completude_confirmada;
  const cls = getCardClasses(pct, tipo_servico);

  return (
    <Card
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
      className={`cursor-pointer border-2 p-4 transition hover:shadow-md ${cls}`}
      data-testid="kit-card"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-bold text-gray-900 leading-tight">{condominio_nome}</h3>
        <Badge variant="outline" className="shrink-0 text-xs">
          {TIPO_LABELS[tipo_servico]}
        </Badge>
      </div>

      {isAdmin ? (
        <div className="mt-4">
          <Badge className="bg-gray-500 text-white">SEM KIT</Badge>
          <p className="mt-2 text-xs text-gray-500">Escritório não possui kit documental</p>
        </div>
      ) : (
        <>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold">{pct.toFixed(1)}%</span>
            <span className="text-sm text-gray-600">confirmado</span>
          </div>
          <Progress value={pct} className="mt-2 h-2" />
          <p className="mt-2 text-sm text-gray-600">
            {metricas.total_presente_confirmado} / {metricas.total_esperado} docs
          </p>
          {metricas.total_presente_pendente_revisao > 0 && (
            <Badge className="mt-2 bg-amber-500 text-white text-xs">
              {metricas.total_presente_pendente_revisao} em revisão
            </Badge>
          )}
        </>
      )}
    </Card>
  );
}
