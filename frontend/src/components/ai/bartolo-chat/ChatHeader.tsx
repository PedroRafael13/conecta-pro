import { X, Minimize2, Maximize2, RotateCcw } from 'lucide-react';
import { DachshundIcon } from './DachshundIcon';

interface ChatHeaderProps {
  isMinimized: boolean;
  onReset: () => void;
  onToggleMinimize: () => void;
  onClose: () => void;
}

export function ChatHeader({ isMinimized, onReset, onToggleMinimize, onClose }: ChatHeaderProps) {
  return (
    <div className="relative flex items-center justify-between px-5 py-4 bg-gradient-to-r from-navy-800 via-navy-700 to-brand-600 overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(255,255,255,0.1),transparent)] pointer-events-none" />

      <div className="flex items-center gap-3 relative z-10">
        <div className="w-10 h-10 rounded-full bg-white/25 backdrop-blur-sm flex items-center justify-center ring-2 ring-white/30 shadow-lg">
          <DachshundIcon className="w-6 h-6" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-white tracking-tight">Bartolo</h3>
            <span className="w-2 h-2 rounded-full bg-green-400 shadow-lg shadow-green-400/50 animate-pulse" />
          </div>
          {!isMinimized && (
            <p className="text-xs text-white/90 font-medium">
              Assistente IA • Online
            </p>
          )}
        </div>
      </div>
      <div className="flex items-center gap-1.5 relative z-10">
        <button
          onClick={onReset}
          className="p-2 rounded-xl hover:bg-white/20 active:bg-white/30 transition-all duration-200 group"
          title="Reiniciar conversa"
        >
          <RotateCcw className="w-4 h-4 text-white group-hover:rotate-180 transition-transform duration-500" />
        </button>
        <button
          onClick={onToggleMinimize}
          className="p-2 rounded-xl hover:bg-white/20 active:bg-white/30 transition-all duration-200 group"
          title={isMinimized ? 'Expandir' : 'Minimizar'}
        >
          {isMinimized ? (
            <Maximize2 className="w-4 h-4 text-white group-hover:scale-110 transition-transform" />
          ) : (
            <Minimize2 className="w-4 h-4 text-white group-hover:scale-110 transition-transform" />
          )}
        </button>
        <button
          onClick={onClose}
          className="p-2 rounded-xl hover:bg-white/20 active:bg-white/30 transition-all duration-200 group"
          title="Fechar"
        >
          <X className="w-4 h-4 text-white group-hover:rotate-90 transition-transform duration-300" />
        </button>
      </div>
    </div>
  );
}
