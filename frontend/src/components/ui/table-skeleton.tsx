export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="divide-y divide-[hsl(var(--border))]">
      {[...Array(rows)].map((_, i) => (
        <div key={i} className="p-4 flex items-center gap-4">
          <div className="flex-1 space-y-2">
            <div className="h-4 w-48 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
            <div className="h-3 w-32 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
          </div>
          <div className="h-6 w-20 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
          <div className="h-4 w-24 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
        </div>
      ))}
    </div>
  );
}
