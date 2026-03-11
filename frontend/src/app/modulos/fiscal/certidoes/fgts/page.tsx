'use client';

import { redirect } from 'next/navigation';

export default function CRFFGTSPage() {
  redirect('/modulos/fiscal/certidoes?tipo=CRF_FGTS');
}
