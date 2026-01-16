import { useEffect, useRef } from 'react';

/**
 * Hook para gerenciar o titulo do documento de forma dinamica.
 * Melhora SEO e UX ao mostrar titulos contextuais.
 *
 * @param title - Titulo da pagina atual
 * @param restoreOnUnmount - Se deve restaurar o titulo anterior ao desmontar (default: true)
 *
 * @example
 * // Na pagina de Dashboard
 * useDocumentTitle('Dashboard');
 * // Resultado: "Dashboard | Conecta PRO"
 *
 * @example
 * // Titulo vazio usa apenas o nome da aplicacao
 * useDocumentTitle('');
 * // Resultado: "Conecta PRO"
 */
export function useDocumentTitle(title: string, restoreOnUnmount: boolean = true) {
  const previousTitleRef = useRef<string>(document.title);

  useEffect(() => {
    const previousTitle = previousTitleRef.current;

    // Define o novo titulo
    document.title = title ? `${title} | Conecta PRO` : 'Conecta PRO';

    return () => {
      if (restoreOnUnmount) {
        document.title = previousTitle;
      }
    };
  }, [title, restoreOnUnmount]);
}

/**
 * Hook para definir titulo do documento sem restaurar ao desmontar.
 * Util para navegacao onde o titulo deve persistir.
 *
 * @param title - Titulo da pagina atual
 */
export function usePageTitle(title: string) {
  useDocumentTitle(title, false);
}

export default useDocumentTitle;
