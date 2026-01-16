import { motion } from 'framer-motion';

interface PageLoaderProps {
  message?: string;
}

export function PageLoader({ message = 'Carregando...' }: PageLoaderProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 bg-conecta-gradient flex flex-col items-center justify-center"
    >
      {/* Logo animation */}
      <div className="relative">
        <motion.div
          animate={{ scale: [1, 1.1, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="w-20 h-20 bg-white rounded-xl flex items-center justify-center shadow-2xl"
        >
          <svg className="w-12 h-12" viewBox="0 0 32 32">
            <motion.path
              d="M6 16L12 22L26 8"
              stroke="#FF6B35"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.8, repeat: Infinity, repeatDelay: 0.5 }}
            />
          </svg>
        </motion.div>
      </div>

      {/* Loading text */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mt-6 text-center"
      >
        <h2 className="text-white font-bold text-xl">
          CONECTA <span className="text-conecta-laranja">PRO</span>
        </h2>
        <p className="text-gray-300 text-sm mt-2">{message}</p>
      </motion.div>

      {/* Loading dots */}
      <div className="flex gap-1.5 mt-4">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="w-2 h-2 bg-white rounded-full"
            animate={{ opacity: [0.3, 1, 0.3] }}
            transition={{
              duration: 1,
              repeat: Infinity,
              delay: i * 0.2,
            }}
          />
        ))}
      </div>
    </motion.div>
  );
}

export default PageLoader;
