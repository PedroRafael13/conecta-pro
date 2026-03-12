'use client';

import { Gift, ArrowLeft, Inbox, Bus, UtensilsCrossed, Heart, Shield, Smile } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const tiposCards = [
  { tipo: 'VT', total: 42, valor: 'R$ 13.860,00', icon: Bus, color: 'text-blue-600', bgColor: 'bg-blue-50' },
  { tipo: 'VR', total: 38, valor: 'R$ 15.200,00', icon: UtensilsCrossed, color: 'text-orange-600', bgColor: 'bg-orange-50' },
  { tipo: 'VA', total: 10, valor: 'R$ 5.500,00', icon: UtensilsCrossed, color: 'text-green-600', bgColor: 'bg-green-50' },
  { tipo: 'Plano Saude', total: 35, valor: 'R$ 24.500,00', icon: Heart, color: 'text-red-600', bgColor: 'bg-red-50' },
  { tipo: 'Odonto', total: 30, valor: 'R$ 4.500,00', icon: Smile, color: 'text-cyan-600', bgColor: 'bg-cyan-50' },
  { tipo: 'Seguro Vida', total: 44, valor: 'R$ 3.520,00', icon: Shield, color: 'text-purple-600', bgColor: 'bg-purple-50' },
];

const statusConfig: Record<string, { label: string; className: string }> = {
  ativo: { label: 'Ativo', className: 'bg-green-500 text-white' },
  inativo: { label: 'Inativo', className: 'bg-gray-500 text-white' },
};

const beneficios = [
  { colaborador: 'Carlos Silva', tipo: 'VT', plano: 'Urbano - 2 linhas', empresa: 264.00, desconto: 158.40, status: 'ativo' },
  { colaborador: 'Carlos Silva', tipo: 'Plano Saude', plano: 'Unimed Enfermaria', empresa: 450.00, desconto: 135.00, status: 'ativo' },
  { colaborador: 'Ana Souza', tipo: 'VR', plano: 'Sodexo R$ 25/dia', empresa: 400.00, desconto: 0, status: 'ativo' },
  { colaborador: 'Ana Souza', tipo: 'Odonto', plano: 'Bradesco Dental', empresa: 45.00, desconto: 15.00, status: 'ativo' },
  { colaborador: 'Pedro Lima', tipo: 'Seguro Vida', plano: 'MetLife Basico', empresa: 80.00, desconto: 0, status: 'ativo' },
];

const fmt = (v: number) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;

export default function BeneficiosPage() {
  const router = useRouter();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => router.push('/modulos/dp')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Gift className="h-6 w-6" />
              Gestao de Beneficios
            </h1>
            <p className="text-muted-foreground">Beneficios oferecidos aos colaboradores</p>
          </div>
        </div>
        <Button size="sm"><Gift className="h-4 w-4 mr-1" /> Novo Beneficio</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
        {tiposCards.map((card) => (
          <Card key={card.tipo}>
            <CardContent className="pt-4 pb-4">
              <div className="flex items-center gap-2 mb-1">
                <div className={`h-8 w-8 rounded-lg ${card.bgColor} flex items-center justify-center`}>
                  <card.icon className={`h-4 w-4 ${card.color}`} />
                </div>
                <span className="text-sm font-medium">{card.tipo}</span>
              </div>
              <p className="text-lg font-bold">{card.total} colab.</p>
              <p className="text-xs text-muted-foreground">{card.valor}/mes</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader><CardTitle>Beneficios por Colaborador</CardTitle></CardHeader>
        <CardContent>
          {beneficios.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Inbox className="h-12 w-12 mb-3" />
              <p>Nenhum beneficio cadastrado</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Colaborador</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Plano</TableHead>
                  <TableHead>Contrib. Empresa</TableHead>
                  <TableHead>Desc. Funcionario</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {beneficios.map((item, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-medium">{item.colaborador}</TableCell>
                    <TableCell>{item.tipo}</TableCell>
                    <TableCell>{item.plano}</TableCell>
                    <TableCell>{fmt(item.empresa)}</TableCell>
                    <TableCell>{fmt(item.desconto)}</TableCell>
                    <TableCell><Badge className={statusConfig[item.status].className}>{statusConfig[item.status].label}</Badge></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
