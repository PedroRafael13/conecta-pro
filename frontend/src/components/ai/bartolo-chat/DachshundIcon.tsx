import { cn } from '@/lib/utils';

export function DachshundIcon({ className = 'w-6 h-6', animate = false }: { className?: string; animate?: boolean }) {
  return (
    <svg
      viewBox="0 0 64 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn(className, animate && 'group')}
    >
      {/* Corpo longo */}
      <ellipse
        cx="32"
        cy="24"
        rx="22"
        ry="10"
        fill="#D2691E"
        stroke="#8B4513"
        strokeWidth="1.5"
      />

      {/* Cabeca */}
      <ellipse
        cx="50"
        cy="22"
        rx="8"
        ry="7"
        fill="#D2691E"
        stroke="#8B4513"
        strokeWidth="1.5"
      />

      {/* Focinho */}
      <ellipse
        cx="56"
        cy="23"
        rx="4"
        ry="3.5"
        fill="#A0522D"
        stroke="#8B4513"
        strokeWidth="1"
      />

      {/* Nariz */}
      <circle cx="58" cy="23" r="1.5" fill="#000" />

      {/* Orelha esquerda */}
      <ellipse
        cx="48"
        cy="16"
        rx="3"
        ry="6"
        fill="#A0522D"
        stroke="#8B4513"
        strokeWidth="1"
        transform="rotate(-15 48 16)"
      />

      {/* Orelha direita */}
      <ellipse
        cx="52"
        cy="16"
        rx="3"
        ry="6"
        fill="#A0522D"
        stroke="#8B4513"
        strokeWidth="1"
        transform="rotate(15 52 16)"
      />

      {/* Olho */}
      <circle cx="52" cy="20" r="1.5" fill="#000" />

      {/* Pernas (4 pernas curtas) */}
      <rect x="18" y="32" width="2.5" height="8" rx="1.25" fill="#8B4513" />
      <rect x="26" y="32" width="2.5" height="8" rx="1.25" fill="#8B4513" />
      <rect x="38" y="32" width="2.5" height="8" rx="1.25" fill="#8B4513" />
      <rect x="46" y="32" width="2.5" height="8" rx="1.25" fill="#8B4513" />

      {/* Patinhas */}
      <ellipse cx="19.25" cy="41" rx="2" ry="1.5" fill="#A0522D" />
      <ellipse cx="27.25" cy="41" rx="2" ry="1.5" fill="#A0522D" />
      <ellipse cx="39.25" cy="41" rx="2" ry="1.5" fill="#A0522D" />
      <ellipse cx="47.25" cy="41" rx="2" ry="1.5" fill="#A0522D" />

      {/* Rabo (com animacao) */}
      <path
        d="M 10 20 Q 8 18 6 20 Q 4 22 5 24"
        stroke="#8B4513"
        strokeWidth="2.5"
        fill="none"
        strokeLinecap="round"
        className={cn(
          animate && 'origin-[10px_20px] group-hover:animate-[wag_0.5s_ease-in-out_infinite]'
        )}
      />
    </svg>
  );
}
