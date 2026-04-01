'use client';

import { redirect } from 'next/navigation';

export default function CNDMunicipalPage() {
  redirect('/modulos/fiscal/certidoes?tipo=CND_MUNICIPAL');
}
