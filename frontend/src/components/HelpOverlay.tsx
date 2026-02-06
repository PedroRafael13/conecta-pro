'use client';

;
import { X } from 'lucide-react';
import type { KeyboardShortcut } from '@/hooks/useKeyboardShortcuts';

interface HelpOverlayProps {
  isOpen: boolean;
  onClose: () => void;
  shortcuts: KeyboardShortcut[];
}

export function HelpOverlay({ isOpen, onClose, shortcuts }: HelpOverlayProps) {
  if (!isOpen) return null;

  const formatKey = (shortcut: KeyboardShortcut): string => {
    const keys: string[] = [];

    if (shortcut.ctrl) keys.push('Ctrl');
    if (shortcut.alt) keys.push('Alt');
    if (shortcut.shift) keys.push('Shift');

    // Capitalizar tecla principal
    const mainKey = shortcut.key === '/' ? '/' :
                   shortcut.key === '?' ? '?' :
                   shortcut.key.length === 1 ? shortcut.key.toUpperCase() :
                   shortcut.key.charAt(0).toUpperCase() + shortcut.key.slice(1);

    keys.push(mainKey);

    return keys.join(' + ');
  };

  // Agrupar shortcuts por categoria
  const categories = {
    'Geral': shortcuts.filter(s =>
      s.key === '/' || s.key === 'k' || s.key === 'b' || s.key === 'Escape' || s.key === '?'
    ),
    'Navegação': shortcuts.filter(s =>
      s.alt && ['1', '2', '3', '4'].includes(s.key)
    ),
    'Ações Contextuais': shortcuts.filter(s =>
      s.key === 'n' || s.key === 's'
    ),
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-full max-w-2xl bg-[hsl(var(--background))] rounded-lg shadow-2xl border border-[hsl(var(--border))] max-h-[80vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[hsl(var(--border))]">
          <div>
            <h2 className="text-lg font-semibold">Atalhos de Teclado</h2>
            <p className="text-sm text-muted-foreground">
              Navegue rapidamente pelo sistema
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-accent rounded transition-colors"
            aria-label="Fechar"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Shortcuts */}
        <div className="overflow-y-auto max-h-[calc(80vh-120px)] px-6 py-4">
          {Object.entries(categories).map(([category, categoryShortcuts]) => {
            if (categoryShortcuts.length === 0) return null;

            return (
              <div key={category} className="mb-6 last:mb-0">
                <h3 className="text-sm font-semibold text-muted-foreground mb-3">
                  {category}
                </h3>
                <div className="space-y-2">
                  {categoryShortcuts.map((shortcut, idx) => (
                    <div
                      key={`${category}-${idx}`}
                      className="flex items-center justify-between py-2 px-3 rounded hover:bg-accent/50 transition-colors"
                    >
                      <span className="text-sm">{shortcut.description}</span>
                      <kbd className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-mono bg-muted border border-border rounded">
                        {formatKey(shortcut)}
                      </kbd>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-[hsl(var(--border))] bg-muted/30">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Pressione <kbd className="px-1.5 py-0.5 bg-background border border-border rounded">Esc</kbd> para fechar</span>
            <span>{shortcuts.length} atalhos disponíveis</span>
          </div>
        </div>
      </div>
    </div>
  );
}
