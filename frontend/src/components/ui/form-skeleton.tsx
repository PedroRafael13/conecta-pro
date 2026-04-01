export function FormSkeleton({ className }: { className?: string }) {
  return (
    <div data-testid="form-skeleton" className={`space-y-4 ${className || ''}`}>
      {[...Array(4)].map((_, i) => (
        <div key={i} className="space-y-2">
          <div className="h-4 w-24 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
          <div className="h-10 w-full bg-[hsl(var(--secondary))] rounded animate-shimmer" />
        </div>
      ))}
      <div className="flex gap-2 justify-end pt-4">
        <div className="h-10 w-24 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
        <div className="h-10 w-24 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
      </div>
    </div>
  );
}
