'use client';

import { redirect } from 'next/navigation';

export default function CNDEstadualPage() {
  redirect('/modulos/fiscal/certidoes?tipo=CND_ESTADUAL');
}
