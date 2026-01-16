import { type ComponentPropsWithoutRef } from 'react';

interface SkipLinkProps extends ComponentPropsWithoutRef<'a'> {
  /** ID do elemento de destino (default: 'main-content') */
  targetId?: string;
  /** Texto do link (default: 'Pular para conteudo principal') */
  label?: string;
}

/**
 * Link de acessibilidade para pular navegacao.
 * Visivel apenas quando recebe foco via teclado.
 * Melhora significativamente a navegacao por teclado.
 *
 * @example
 * // No topo do layout
 * <SkipLink />
 *
 * // O elemento de destino deve ter o id correspondente
 * <main id="main-content">...</main>
 *
 * @example
 * // Com destino customizado
 * <SkipLink targetId="content-area" label="Ir para area de conteudo" />
 */
export function SkipLink({
  targetId = 'main-content',
  label = 'Pular para conteudo principal',
  className = '',
  ...props
}: SkipLinkProps) {
  return (
    <a
      href={`#${targetId}`}
      className={`
        sr-only focus:not-sr-only
        focus:fixed focus:top-4 focus:left-4 focus:z-[9999]
        focus:px-4 focus:py-2
        focus:bg-primary-600 focus:text-white
        focus:rounded-lg focus:shadow-lg
        focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-primary-600
        transition-all duration-200
        font-medium text-sm
        ${className}
      `.trim()}
      {...props}
    >
      {label}
    </a>
  );
}

/**
 * Componente para multiplos skip links.
 * Util quando ha varias areas navegaveis.
 *
 * @example
 * <SkipLinks
 *   links={[
 *     { targetId: 'main-content', label: 'Ir para conteudo' },
 *     { targetId: 'sidebar', label: 'Ir para navegacao' },
 *   ]}
 * />
 */
export function SkipLinks({
  links,
}: {
  links: Array<{ targetId: string; label: string }>;
}) {
  return (
    <div className="skip-links">
      {links.map((link, index) => (
        <SkipLink
          key={link.targetId}
          targetId={link.targetId}
          label={link.label}
          style={{ top: `${1 + index * 3}rem` }}
        />
      ))}
    </div>
  );
}

export type { SkipLinkProps };
export default SkipLink;
