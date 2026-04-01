'use client';

import { redirect } from 'next/navigation';

export default function CNDTPage() {
  redirect('/modulos/fiscal/certidoes?tipo=CND_TRABALHISTA');
}
