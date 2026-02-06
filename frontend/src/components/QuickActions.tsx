'use client';

;
import { Plus, FileWarning, UserPlus, MapPin, FileText } from 'lucide-react';
import { useState } from 'react';
import { Button } from './ui/button';

export function QuickActions() {
  const [isOpen, setIsOpen] = useState(false);

  const actions = [
    { icon: FileWarning, label: 'Nova Ocorrência', onClick: () => {} },
    { icon: UserPlus, label: 'Adicionar Colaborador', onClick: () => {} },
    { icon: MapPin, label: 'Criar Posto', onClick: () => {} },
    { icon: FileText, label: 'Gerar Relatório', onClick: () => {} },
  ];

  return (
    <div className="relative" data-tour="quick-actions">
      <Button
        variant="default"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="gap-2"
      >
        <Plus className="w-4 h-4" />
        <span className="hidden sm:inline">Ações Rápidas</span>
      </Button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 z-50">
            <div className="p-2">
              <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 px-3 py-2">
                AÇÕES RÁPIDAS
              </p>
              {actions.map((action, index) => {
                const Icon = action.icon;
                return (
                  <button
                    key={index}
                    onClick={() => {
                      action.onClick();
                      setIsOpen(false);
                    }}
                    className="w-full flex items-center gap-3 px-3 py-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <Icon className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      {action.label}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
