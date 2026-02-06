export function FormSkeleton() {
  return (
    <div className="space-y-4">
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
