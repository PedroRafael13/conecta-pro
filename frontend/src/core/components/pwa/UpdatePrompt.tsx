'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw } from 'lucide-react';
import { usePWA } from '@core/hooks';

export function UpdatePrompt() {
  const { isUpdateAvailable, update } = usePWA();

  return (
    <AnimatePresence>
      {isUpdateAvailable && (
        <motion.div
          initial={{ y: -100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -100, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="fixed top-0 left-0 right-0 z-[100] bg-accent-primary text-white px-4 py-3 shadow-lg"
        >
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3">
              <RefreshCw className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">
                Nova versao disponivel!
              </span>
            </div>
            <button
              onClick={update}
              className="px-4 py-1.5 bg-white/20 hover:bg-white/30 text-sm font-medium rounded-lg transition-colors"
            >
              Atualizar agora
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
