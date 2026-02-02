export function ChartSkeleton({ height = 300 }: { height?: number }) {
  return (
    <div
      className="flex items-center justify-center bg-[hsl(var(--secondary))]/20 rounded-lg"
      style={{ height: `${height}px` }}
    >
      <div className="animate-pulse text-[hsl(var(--muted-foreground))] text-sm">
        Carregando gráfico...
      </div>
    </div>
  );
}
