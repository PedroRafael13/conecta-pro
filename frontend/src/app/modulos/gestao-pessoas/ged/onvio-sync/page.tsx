import type { Metadata } from 'next';

import OnvioSyncDashboard from './onvio-sync-dashboard';

export const metadata: Metadata = {
  title: 'GEDEON — Onvio Sync | Conecta PRO',
  description: 'Documentos da Portte Contábil sincronizados automaticamente',
};

export default function OnvioSyncPage() {
  return <OnvioSyncDashboard />;
}
