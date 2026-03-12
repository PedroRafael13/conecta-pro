'use client';

import { BookOpen, Plus, Clock, Users, CheckCircle, XCircle } from 'lucide-react';
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const cursosMock = [
  { id: 1, nome: 'Vigilancia Patrimonial - Basico', categoria: 'Obrigatorio Seguranca', duracao: '40h', participantes: 28, status: 'Ativo', obrigatorio: true },
  { id: 2, nome: 'Primeiros Socorros', categoria: 'Obrigatorio Seguranca', duracao: '16h', participantes: 35, status: 'Ativo', obrigatorio: true },
  { id: 3, nome: 'Gestao de Conflitos', categoria: 'Comportamental', duracao: '8h', participantes: 12, status: 'Ativo', obrigatorio: false },
  { id: 4, nome: 'CFTV e Monitoramento', categoria: 'Tecnico', duracao: '24h', participantes: 18, status: 'Ativo', obrigatorio: false },
  { id: 5, nome: 'Combate a Incendio', categoria: 'Obrigatorio Seguranca', duracao: '20h', participantes: 30, status: 'Ativo', obrigatorio: true },
  { id: 6, nome: 'Comunicacao Eficaz', categoria: 'Comportamental', duracao: '4h', participantes: 0, status: 'Inativo', obrigatorio: false },
];

const categoriaCores: Record<string, string> = {
  'Obrigatorio Seguranca': 'bg-red-900/30 text-red-400',
  'Tecnico': 'bg-blue-900/30 text-blue-400',
  'Comportamental': 'bg-green-900/30 text-green-400',
};

export default function CursosPage() {
  const [cursos] = useState(cursosMock);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <BookOpen className="h-6 w-6" />
            Catalogo de Cursos
          </h1>
          <p className="text-muted-foreground">Cursos disponiveis para treinamento</p>
        </div>
        <Button><Plus className="h-4 w-4 mr-2" />Novo Curso</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {cursos.map((curso) => (
          <Card key={curso.id} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium">{curso.nome}</CardTitle>
                {curso.obrigatorio && (
                  <span className="text-xs bg-red-900/30 text-red-400 px-2 py-0.5 rounded">Obrigatorio</span>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <span className={`text-xs px-2 py-0.5 rounded ${categoriaCores[curso.categoria] || 'bg-gray-800 text-gray-400'}`}>
                {curso.categoria}
              </span>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{curso.duracao}</span>
                <span className="flex items-center gap-1"><Users className="h-3 w-3" />{curso.participantes}</span>
              </div>
              <div className="flex items-center gap-1 text-sm">
                {curso.status === 'Ativo' ? (
                  <><CheckCircle className="h-4 w-4 text-green-500" /><span className="text-green-500">Ativo</span></>
                ) : (
                  <><XCircle className="h-4 w-4 text-gray-500" /><span className="text-gray-500">Inativo</span></>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
