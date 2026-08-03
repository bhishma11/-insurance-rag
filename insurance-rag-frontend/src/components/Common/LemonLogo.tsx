import React from 'react';

interface LemonLogoProps {
  size?: number;
  className?: string;
  animated?: boolean;
}

export const LemonLogo: React.FC<LemonLogoProps> = ({ 
  size = 48, 
  className = '',
  animated = true 
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`${className} ${animated ? 'hover:scale-105 transition-transform duration-300' : ''}`}
    >
      {/* Lemon Body */}
      <ellipse cx="50" cy="50" rx="35" ry="30" fill="url(#lemonGrad)" stroke="#d69e2e" strokeWidth="2"/>
      
      {/* Lemon Texture */}
      <ellipse cx="42" cy="44" rx="14" ry="9" fill="white" opacity="0.15"/>
      <ellipse cx="58" cy="56" rx="10" ry="6" fill="white" opacity="0.1"/>
      <ellipse cx="48" cy="52" rx="8" ry="5" fill="white" opacity="0.08"/>
      
      {/* Lemon Highlights */}
      <ellipse cx="38" cy="40" rx="6" ry="4" fill="white" opacity="0.25"/>
      <ellipse cx="62" cy="58" rx="4" ry="3" fill="white" opacity="0.15"/>
      
      {/* Lemon Stem */}
      <rect x="46" y="16" width="8" height="14" rx="3" fill="#68a30d"/>
      <ellipse cx="50" cy="16" rx="5" ry="4" fill="#4d7c0f"/>
      
      {/* Lemon Leaf */}
      <ellipse cx="60" cy="20" rx="10" ry="6" fill="#84cc16" transform="rotate(25 60 20)"/>
      <line x1="60" y1="16" x2="60" y2="24" stroke="#65a30d" strokeWidth="1.5"/>
      
      {/* Face - Friendly */}
      <circle cx="40" cy="46" r="5" fill="#1a202c"/>
      <circle cx="60" cy="46" r="5" fill="#1a202c"/>
      <circle cx="41" cy="44" r="2" fill="white"/>
      <circle cx="61" cy="44" r="2" fill="white"/>
      
      {/* Eyebrows */}
      <path d="M34 38 Q40 33 46 38" stroke="#1a202c" strokeWidth="2" fill="none"/>
      <path d="M54 38 Q60 33 66 38" stroke="#1a202c" strokeWidth="2" fill="none"/>
      
      {/* Smile */}
      <path d="M42 58 Q50 68 58 58" stroke="#1a202c" strokeWidth="2.5" fill="none" strokeLinecap="round"/>
      
      {/* Blush */}
      <ellipse cx="34" cy="54" rx="8" ry="4" fill="#fc8181" opacity="0.2"/>
      <ellipse cx="66" cy="54" rx="8" ry="4" fill="#fc8181" opacity="0.2"/>
      
      {/* Sparkle */}
      <g opacity="0.6">
        <path d="M80 20 L82 24 L86 26 L82 28 L80 32 L78 28 L74 26 L78 24 Z" fill="#f6e05e"/>
        <path d="M20 70 L21 72 L23 73 L21 74 L20 76 L19 74 L17 73 L19 72 Z" fill="#f6e05e"/>
      </g>
      
      <defs>
        <linearGradient id="lemonGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#fef08a"/>
          <stop offset="40%" stopColor="#facc15"/>
          <stop offset="100%" stopColor="#eab308"/>
        </linearGradient>
      </defs>
    </svg>
  );
};

export default LemonLogo;