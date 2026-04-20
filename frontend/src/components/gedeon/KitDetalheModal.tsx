'use client';

import type { CompletudeKit, MotivoFaltante } from '@/types/kit-completude';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';

const MOTIVO_LABELS: Record<MotivoFaltante, string> = {
  nao_encontrado_onvio: 'Não sincronizado do Onvio',
  aguarda_fase_1_cnd: 'Aguarda busca automática CND (FASE 1)',
  aguarda_fase_2_banco: 'Aguarda integração bancária (FASE 2)',
  nao_sincronizado: 'Não sincronizado',
};

interface KitDetalheModalProps {
  kit: CompletudeKit | null;
  open: boolean;
  onClose: () => void;
}

export function KitDetalheModal({ kit, open, onClose }: KitDetalheModalProps) {
  if (!kit) return null;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {kit.condominio_nome} — {kit.mes_ref}
          </DialogTitle>
        </DialogHeader>

        <div className="mb-3 flex gap-3 text-sm text-gray-600">
          <span>Esperado: <strong>{kit.metricas.total_esperado}</strong></span>
          <span>Presentes: <strong>{kit.metricas.total_presente_confirmado}</strong></span>
          <span>Faltantes: <strong>{kit.metricas.total_faltante}</strong></span>
          <span>Completude: <strong>{kit.metricas.pct_completude_confirmada.toFixed(1)}%</strong></span>
        </div>

        <Tabs defaultValue="presentes">
          <TabsList>
            <TabsTrigger value="presentes">
              Docs Presentes ({kit.docs_presentes.length})
            </TabsTrigger>
            <TabsTrigger value="faltantes">
              Docs Faltantes ({kit.docs_faltantes.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="presentes">
            {kit.docs_presentes.length === 0 ? (
              <p className="py-6 text-center text-sm text-gray-500">Nenhum documento presente.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="p-2 text-left font-medium">Tipo</th>
                      <th className="p-2 text-left font-medium">Escopo</th>
                      <th className="p-2 text-left font-medium">Arquivo</th>
                      <th className="p-2 text-left font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {kit.docs_presentes.map((d) => (
                      <tr key={d.onvio_document_id} className="border-t">
                        <td className="p-2">{d.tipo_documento}</td>
                        <td className="p-2 text-gray-500">{d.escopo}</td>
                        <td className="p-2 max-w-xs truncate text-gray-700">{d.nome_arquivo}</td>
                        <td className="p-2">
                          {d.revisao_pendente ? (
                            <Badge className="bg-amber-100 text-amber-800 border-amber-300">
                              Revisão
                            </Badge>
                          ) : (
                            <Badge className="bg-green-100 text-green-800 border-green-300">
                              OK
                            </Badge>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </TabsContent>

          <TabsContent value="faltantes">
            {kit.docs_faltantes.length === 0 ? (
              <p className="py-6 text-center text-sm text-gray-500">
                Todos os documentos estão presentes.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="p-2 text-left font-medium">Tipo</th>
                      <th className="p-2 text-left font-medium">Escopo</th>
                      <th className="p-2 text-left font-medium">Motivo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {kit.docs_faltantes.map((d, i) => (
                      <tr key={`${d.tipo_documento}-${i}`} className="border-t">
                        <td className="p-2">{d.tipo_documento}</td>
                        <td className="p-2 text-gray-500">{d.escopo}</td>
                        <td className="p-2 text-gray-600">{MOTIVO_LABELS[d.motivo]}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
