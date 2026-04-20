type ClientLike = { name?: string | null; trading_name?: string | null; cnpj?: string | null } | null | undefined;

export const clientLabel = (c: ClientLike): string =>
  c?.name || c?.trading_name || c?.cnpj || '—';
