import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Folha de Pagamento',
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
