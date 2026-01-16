import { useCallback, useEffect, useRef } from 'react';

type AriaLivePoliteness = 'polite' | 'assertive' | 'off';

interface AnnounceOptions {
  /** Politeness level do anuncio */
  politeness?: AriaLivePoliteness;
  /** Tempo em ms para limpar o anuncio (default: 1000) */
  clearDelay?: number;
}

/**
 * Hook para anunciar mudancas para screen readers usando aria-live regions.
 * Cria uma regiao invisivel que screen readers monitoram para anuncios.
 *
 * @param defaultPoliteness - Nivel padrao de politeness ('polite' ou 'assertive')
 *
 * @returns Funcao announce para fazer anuncios
 *
 * @example
 * const announce = useAnnounce();
 *
 * // Anuncio educado (nao interrompe)
 * announce('Item adicionado ao carrinho');
 *
 * // Anuncio assertivo (interrompe imediatamente)
 * announce('Erro ao salvar', { politeness: 'assertive' });
 *
 * @example
 * // Anunciar mudanca de pagina
 * useEffect(() => {
 *   announce(`Navegou para ${pageTitle}`);
 * }, [pageTitle, announce]);
 */
export function useAnnounce(defaultPoliteness: AriaLivePoliteness = 'polite') {
  // Refs para os elementos de live region
  const politeRef = useRef<HTMLDivElement | null>(null);
  const assertiveRef = useRef<HTMLDivElement | null>(null);

  // Cria as live regions no mount
  useEffect(() => {
    // Container para as live regions
    let container = document.getElementById('aria-live-container');

    if (!container) {
      container = document.createElement('div');
      container.id = 'aria-live-container';
      container.style.cssText = `
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
      `;
      document.body.appendChild(container);
    }

    // Cria regiao polite se nao existir
    let politeRegion = document.getElementById('aria-live-polite');
    if (!politeRegion) {
      politeRegion = document.createElement('div');
      politeRegion.id = 'aria-live-polite';
      politeRegion.setAttribute('aria-live', 'polite');
      politeRegion.setAttribute('aria-atomic', 'true');
      politeRegion.setAttribute('role', 'status');
      container.appendChild(politeRegion);
    }
    politeRef.current = politeRegion as HTMLDivElement;

    // Cria regiao assertive se nao existir
    let assertiveRegion = document.getElementById('aria-live-assertive');
    if (!assertiveRegion) {
      assertiveRegion = document.createElement('div');
      assertiveRegion.id = 'aria-live-assertive';
      assertiveRegion.setAttribute('aria-live', 'assertive');
      assertiveRegion.setAttribute('aria-atomic', 'true');
      assertiveRegion.setAttribute('role', 'alert');
      container.appendChild(assertiveRegion);
    }
    assertiveRef.current = assertiveRegion as HTMLDivElement;

    // Cleanup - nao remove pois outras instancias podem estar usando
    return () => {
      // Limpa conteudo ao desmontar
      if (politeRef.current) politeRef.current.textContent = '';
      if (assertiveRef.current) assertiveRef.current.textContent = '';
    };
  }, []);

  // Funcao para fazer anuncios
  const announce = useCallback(
    (message: string, options: AnnounceOptions = {}) => {
      const { politeness = defaultPoliteness, clearDelay = 1000 } = options;

      if (politeness === 'off') return;

      const region =
        politeness === 'assertive' ? assertiveRef.current : politeRef.current;

      if (region) {
        // Limpa primeiro para garantir que mudancas sejam anunciadas
        region.textContent = '';

        // Usa setTimeout para garantir que o DOM atualize
        requestAnimationFrame(() => {
          region.textContent = message;

          // Limpa apos delay para permitir novos anuncios
          setTimeout(() => {
            if (region) region.textContent = '';
          }, clearDelay);
        });
      }
    },
    [defaultPoliteness]
  );

  return announce;
}

/**
 * Hook que anuncia automaticamente quando uma variavel muda.
 *
 * @param value - Valor a monitorar
 * @param getMessage - Funcao que retorna a mensagem baseada no valor
 * @param options - Opcoes do anuncio
 *
 * @example
 * // Anuncia quando contador muda
 * useAnnounceOnChange(count, (val) => `Contador: ${val}`);
 *
 * @example
 * // Anuncia erros de forma assertiva
 * useAnnounceOnChange(error, (err) => err?.message || '', {
 *   politeness: 'assertive',
 * });
 */
export function useAnnounceOnChange<T>(
  value: T,
  getMessage: (value: T) => string,
  options: AnnounceOptions = {}
) {
  const announce = useAnnounce();
  const isFirstRender = useRef(true);

  useEffect(() => {
    // Pula primeiro render
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    const message = getMessage(value);
    if (message) {
      announce(message, options);
    }
  }, [value, getMessage, announce, options]);
}

export default useAnnounce;
