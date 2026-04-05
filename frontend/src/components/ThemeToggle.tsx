'use client';

import { Moon, Sun, Monitor, LucideIcon } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { useState, useRef, useEffect } from 'react';

// Mapa de ícones fora do componente para evitar criação durante render
const themeOptions: Array<{ value: string; label: string; icon: LucideIcon }> = [
  { value: 'light', label: 'Claro', icon: Sun },
  { value: 'dark', label: 'Escuro', icon: Moon },
  { value: 'system', label: 'Sistema', icon: Monitor },
];

export function ThemeToggle() {
  const { theme, resolvedTheme, setTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => { setMounted(true); }, []);

  // Fechar dropdown ao clicar fora
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  // Antes do mount, renderizar placeholder neutro para evitar hydration mismatch
  if (!mounted) {
    return <div className="w-10 h-10 rounded-lg bg-[hsl(var(--secondary))] border border-[hsl(var(--border))]" />;
  }

  // Determinar qual ícone renderizar baseado no tema resolvido
  const CurrentIcon = resolvedTheme === 'dark' ? Moon : Sun;
  const currentLabel = themeOptions.find(opt => opt.value === theme)?.label || 'Sistema';

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Botão principal */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative w-10 h-10 rounded-lg bg-[hsl(var(--secondary))] hover:bg-[hsl(var(--muted))] border border-[hsl(var(--border))] flex items-center justify-center transition-all duration-200 group"
        aria-label="Toggle theme"
        title={`Tema: ${currentLabel}`}
      >
        <CurrentIcon className="w-5 h-5 text-[hsl(var(--foreground))] transition-transform duration-200 group-hover:rotate-12" />

        {/* Indicador de tema system */}
        {theme === 'system' && (
          <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-[hsl(var(--primary))] border-2 border-[hsl(var(--card))]" />
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 py-2 bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl shadow-xl z-50 animate-fade-in">
          <div className="px-3 py-2 border-b border-[hsl(var(--border))]">
            <p className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
              Tema
            </p>
          </div>

          {themeOptions.map((option) => {
            const OptionIcon = option.icon;
            const isActive = theme === option.value;

            return (
              <button
                key={option.value}
                onClick={() => {
                  setTheme(option.value as 'light' | 'dark' | 'system');
                  setIsOpen(false);
                }}
                className={`w-full flex items-center gap-3 px-3 py-2.5 text-sm transition-colors ${
                  isActive
                    ? 'bg-[hsl(var(--primary))]/10 text-[hsl(var(--primary))]'
                    : 'text-[hsl(var(--foreground))] hover:bg-[hsl(var(--muted))]'
                }`}
              >
                <OptionIcon className="w-4 h-4 flex-shrink-0" />
                <span className="flex-1 text-left font-medium">{option.label}</span>
                {isActive && (
                  <div className="w-1.5 h-1.5 rounded-full bg-[hsl(var(--primary))]" />
                )}
              </button>
            );
          })}

          {/* Info do tema resolvido */}
          {theme === 'system' && (
            <div className="mx-3 mt-2 pt-2 border-t border-[hsl(var(--border))]">
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                Sistema detectado: <span className="font-medium capitalize">{resolvedTheme}</span>
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Versão compacta (apenas ícone alternando)
export function ThemeToggleCompact() {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);

  if (!mounted) {
    return <div className="w-10 h-10 rounded-lg bg-[hsl(var(--secondary))] border border-[hsl(var(--border))]" />;
  }

  const toggleTheme = () => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark');
  };

  return (
    <button
      onClick={toggleTheme}
      className="w-10 h-10 rounded-lg bg-[hsl(var(--secondary))] hover:bg-[hsl(var(--muted))] border border-[hsl(var(--border))] flex items-center justify-center transition-all duration-200 group"
      aria-label="Toggle theme"
    >
      {resolvedTheme === 'dark' ? (
        <Sun className="w-5 h-5 text-[hsl(var(--foreground))] transition-transform duration-200 group-hover:rotate-90" />
      ) : (
        <Moon className="w-5 h-5 text-[hsl(var(--foreground))] transition-transform duration-200 group-hover:-rotate-12" />
      )}
    </button>
  );
}
