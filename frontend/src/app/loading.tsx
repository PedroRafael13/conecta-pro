import { Loader2 } from 'lucide-react';

export default function RootLoading() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center gap-4">
      <Loader2 className="w-8 h-8 animate-spin text-[hsl(var(--primary))]" />
      <p className="text-sm text-[hsl(var(--muted-foreground))]">Carregando...</p>
    </div>
  );
}
