'use client';

import { Package, ShoppingCart, ArrowRight, Warehouse, TrendingDown, ClipboardList } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { useRouter } from 'next/navigation';

const navigationCards = [
  {
    title: 'Compras',
    description: 'Requisições, cotações e pedidos de compra',
    href: '/modulos/financeiro/compras',
    icon: ShoppingCart,
  },
  {
    title: 'Estoque',
    description: 'Controle de materiais, EPIs e movimentações',
    href: '/modulos/financeiro/estoque',
    icon: Package,
  },
];

export default function SuprimentosPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-grid">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[hsl(var(--background))]/80 backdrop-blur-xl border-b border-[hsl(var(--border))]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4 h-16">
            <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
              <Package className="w-5 h-5 text-amber-500" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-[hsl(var(--foreground))]">Suprimentos</h1>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">Compras, estoque e gestão de materiais</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {navigationCards.map((card) => {
            const Icon = card.icon;
            return (
              <Card
                key={card.href}
                variant="interactive"
                className="group"
                onClick={() => router.push(card.href)}
              >
                <CardContent className="pt-4">
                  <div className="flex flex-col gap-3">
                    <div className="flex items-center justify-between">
                      <div className="w-10 h-10 rounded-lg bg-[hsl(var(--primary))]/10 flex items-center justify-center">
                        <Icon className="w-5 h-5 text-[hsl(var(--primary))]" />
                      </div>
                      <ArrowRight className="w-4 h-4 text-[hsl(var(--muted-foreground))] transition-transform group-hover:translate-x-1" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-[hsl(var(--foreground))]">{card.title}</h3>
                      <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1 line-clamp-2">{card.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </main>
    </div>
  );
}
