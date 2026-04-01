import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Portal do Funcionário — Conecta PRO',
  description: 'Acesse seus contracheques, férias, documentos e treinamentos.',
};

export default function PortalFuncionarioLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
