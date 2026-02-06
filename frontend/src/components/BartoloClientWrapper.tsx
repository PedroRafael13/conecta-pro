'use client';

import dynamic from 'next/dynamic';

const BartoloChat = dynamic(
  () => import('@/components/BartoloChat').then(mod => mod.BartoloChat),
  { ssr: false }
);

export function BartoloClientWrapper() {
  return <BartoloChat />;
}
