import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Departamento Pessoal',
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
