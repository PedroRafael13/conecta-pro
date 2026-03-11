'use client';

import { Landmark } from 'lucide-react';
import { redirect } from 'next/navigation';

export default function CNDFederalPage() {
  // Redireciona para o painel de certidões com filtro federal
  redirect('/modulos/fiscal/certidoes?tipo=CND_FEDERAL');
}
