---
title: Frontend Development
description: Next.js 16 + React 19 + TypeScript 5.9 para Conecta PRO
stack: [nextjs, react, typescript, tailwind]
---

# frontend-dev

Next.js 16 + React 19 + TypeScript 5.9

## Uso

```yaml
skills:
  - frontend-dev
```

---

## Arquitetura de Hooks

```
Page → Root Hook → Wrapper → Orval Hook → customInstance
```

### Exemplo
```typescript
// app/modulos/crm/page.tsx
export default function CRMPage() {
  const { clients, isLoading } = useCRM();
  if (isLoading) return <LoadingState />;
  return <ClientList data={clients} />;
}

// hooks/useCRM.ts (consolidado)
export function useCRM() {
  const { data: clients, isLoading } = useGetClients();
  const createClient = useCreateClient();
  return { clients, isLoading, createClient };
}
```

---

## Componentes

### Padrão
```typescript
// components/ui/button.tsx
import { cn } from "@/lib/utils";

interface ButtonProps {
  variant?: "default" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
  children: React.ReactNode;
}

export function Button({
  variant = "default",
  size = "md",
  children,
  className,
  ...props
}: ButtonProps & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={cn(
        "rounded-md font-medium transition-colors",
        variant === "default" && "bg-primary text-white",
        size === "sm" && "px-2 py-1 text-sm",
        size === "md" && "px-4 py-2",
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
```

---

## Forms (RHF + Zod)

```typescript
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

const schema = z.object({
  name: z.string().min(3),
  email: z.string().email(),
});

export function ClientForm() {
  const form = useForm({
    resolver: zodResolver(schema),
  });

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <Input {...form.register("name")} />
      {form.formState.errors.name && (
        <FormError message={form.formState.errors.name.message} />
      )}
    </form>
  );
}
```

---

## Estado

- **Servidor:** React Query (TanStack Query)
- **Cliente:** Zustand
- **Forms:** React Hook Form

---

## Comandos

```bash
npm run dev
npm run build
npm run test:coverage
npm run type-check
npm run lint
```
