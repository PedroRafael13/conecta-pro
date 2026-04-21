'use client';

import { useState } from 'react';
import { useKitsLote } from '@/hooks/useKitsCompletude';
import { KitCard } from '@/components/gedeon/KitCard';
import { KitDetalheModal } from '@/components/gedeon/KitDetalheModal';
import { KitKPIs } from '@/components/gedeon/KitKPIs';
import { MesRefSelector } from '@/components/gedeon/MesRefSelector';
import type { CompletudeKit } from '@/types/kit-completude';

function defaultMesRef(): string {
  const d = new Date();
  return `${String(d.getMonth() + 1).padStart(2, '0')}.${d.getFullYear()}`;
}

export default function KitsCompletudeePage() {
  const [mesRef, setMesRef] = useState(defaultMesRef);
  const [selected, setSelected] = useState<CompletudeKit | null>(null);
  const { data: kits, isLoading, error } = useKitsLote(mesRef);

  return (
    <div className="container mx-auto p-6">
      {/* Header */}
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-[#0A2540]">Completude Kit Documental</h1>
          <p className="text-gray-600">Status dos kits documentais por condomínio</p>
          <span className="inline-block mt-1 text-xs text-blue-600 bg-blue-50 border border-blue-200 rounded px-2 py-0.5">
            GEDEON CORE — Completude via Onvio
          </span>
        </div>
        <MesRefSelector value={mesRef} onChange={setMesRef} />
      </div>

      {/* Estados de loading / erro */}
      {isLoading && (
        <div className="py-16 text-center text-gray-500">Carregando kits...</div>
      )}
      {error && (
        <div className="py-16 text-center text-red-600">
          Erro ao carregar kits. Tente novamente.
        </div>
      )}

      {/* Conteúdo principal */}
      {kits && (
        <>
          {/* KPIs */}
          <KitKPIs kits={kits} />

          {/* Grid de cards */}
          <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {kits.map((kit) => (
              <KitCard key={kit.condominio_id} kit={kit} onClick={() => setSelected(kit)} />
            ))}
          </div>

          {/* Modal de detalhe */}
          <KitDetalheModal
            kit={selected}
            open={!!selected}
            onClose={() => setSelected(null)}
          />
        </>
      )}
    </div>
  );
}
