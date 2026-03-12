'use client';

import { GraduationCap, Plus, Calendar, MapPin, User } from 'lucide-react';
import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const treinamentosMock = [
  { id: 1, curso: 'Vigilancia Patrimonial - Basico', dataInicio: '2026-03-15', dataFim: '2026-03-25', local: 'Sala 1 - Sede', instrutor: 'Carlos Mendes', participantes: 15, status: 'Agendado' },
  { id: 2, curso: 'Primeiros Socorros', dataInicio: '2026-03-01', dataFim: '2026-03-10', local: 'Centro de Treinamento', instrutor: 'Ana Beatriz', participantes: 20, status: 'Em Andamento' },
  { id: 3, curso: 'CFTV e Monitoramento', dataInicio: '2026-02-10', dataFim: '2026-02-20', local: 'Lab Tecnico', instrutor: 'Roberto Lima', participantes: 12, status: 'Concluido' },
  { id: 4, curso: 'Combate a Incendio', dataInicio: '2026-04-01', dataFim: '2026-04-05', local: 'Area Externa', instrutor: 'Marcos Silva', participantes: 25, status: 'Agendado' },
  { id: 5, curso: 'Gestao de Conflitos', dataInicio: '2026-02-20', dataFim: '2026-02-21', local: 'Sala 2 - Sede', instrutor: 'Patricia Costa', participantes: 10, status: 'Concluido' },
];

const statusCores: Record<string, string> = {
  'Agendado': 'bg-blue-900/30 text-blue-400',
  'Em Andamento': 'bg-yellow-900/30 text-yellow-400',
  'Concluido': 'bg-green-900/30 text-green-400',
};

export default function TreinamentosPage() {
  const [treinamentos] = useState(treinamentosMock);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <GraduationCap className="h-6 w-6" />
            Treinamentos
          </h1>
          <p className="text-muted-foreground">Agenda e gestao de treinamentos</p>
        </div>
        <Button><Plus className="h-4 w-4 mr-2" />Agendar Treinamento</Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left p-4 text-muted-foreground font-medium">Curso</th>
                  <th className="text-left p-4 text-muted-foreground font-medium">Data Inicio</th>
                  <th className="text-left p-4 text-muted-foreground font-medium">Data Fim</th>
                  <th className="text-left p-4 text-muted-foreground font-medium">Local</th>
                  <th className="text-left p-4 text-muted-foreground font-medium">Instrutor</th>
                  <th className="text-center p-4 text-muted-foreground font-medium">Participantes</th>
                  <th className="text-center p-4 text-muted-foreground font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {treinamentos.map((t) => (
                  <tr key={t.id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                    <td className="p-4 font-medium">{t.curso}</td>
                    <td className="p-4 text-muted-foreground">{t.dataInicio}</td>
                    <td className="p-4 text-muted-foreground">{t.dataFim}</td>
                    <td className="p-4 text-muted-foreground flex items-center gap-1"><MapPin className="h-3 w-3" />{t.local}</td>
                    <td className="p-4 text-muted-foreground">{t.instrutor}</td>
                    <td className="p-4 text-center">{t.participantes}</td>
                    <td className="p-4 text-center">
                      <span className={`text-xs px-2 py-1 rounded ${statusCores[t.status]}`}>{t.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
