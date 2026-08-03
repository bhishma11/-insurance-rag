// src/components/Common/LemonMascotLogo.tsx
import React from 'react';

interface LemonMascotLogoProps {
  size?: number;
  className?: string;
}

export const LemonMascotLogo = ({ size = 40, className = '' }: LemonMascotLogoProps) => {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 100 120" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* ===== LEMON HEAD ===== */}
      {/* Lemon Body */}
      <ellipse cx="50" cy="35" rx="32" ry="28" fill="url(#lemonGrad)" stroke="#eab308" strokeWidth="2"/>
      
      {/* Lemon Texture/Lines */}
      <ellipse cx="45" cy="30" rx="12" ry="8" fill="white" opacity="0.15"/>
      <ellipse cx="55" cy="40" rx="8" ry="5" fill="white" opacity="0.1"/>
      
      {/* Lemon Stem */}
      <rect x="47" y="5" width="6" height="12" rx="2" fill="#65a30d"/>
      <ellipse cx="50" cy="5" rx="4" ry="3" fill="#4d7c0f"/>
      
      {/* Lemon Leaf */}
      <ellipse cx="58" cy="8" rx="8" ry="5" fill="#84cc16" transform="rotate(25 58 8)"/>
      <line x1="58" y1="5" x2="58" y2="12" stroke="#65a30d" strokeWidth="1"/>
      
      {/* ===== FACE ===== */}
      {/* Eyes */}
      <circle cx="40" cy="30" r="4" fill="#1e293b"/>
      <circle cx="60" cy="30" r="4" fill="#1e293b"/>
      <circle cx="41" cy="29" r="1.5" fill="white"/>
      <circle cx="61" cy="29" r="1.5" fill="white"/>
      
      {/* Eyebrows */}
      <path d="M35 24 Q40 20 45 24" stroke="#1e293b" strokeWidth="1.5" fill="none"/>
      <path d="M55 24 Q60 20 65 24" stroke="#1e293b" strokeWidth="1.5" fill="none"/>
      
      {/* Mouth - Friendly Smile */}
      <path d="M42 42 Q50 50 58 42" stroke="#1e293b" strokeWidth="2" fill="none" strokeLinecap="round"/>
      <path d="M44 43 Q50 47 56 43" fill="#fcd34d" opacity="0.5"/>
      
      {/* ===== NECK ===== */}
      <rect x="42" y="60" width="16" height="8" rx="2" fill="#fbbf24" stroke="#eab308" strokeWidth="1"/>
      
      {/* ===== HUMAN BODY (Shirt) ===== */}
      <rect x="30" y="66" width="40" height="32" rx="6" fill="url(#shirtGrad)" stroke="#2563eb" strokeWidth="1.5"/>
      
      {/* Collar */}
      <path d="M38 66 L50 74 L62 66" stroke="#1d4ed8" strokeWidth="1.5" fill="none"/>
      
      {/* Tie */}
      <rect x="47" y="68" width="6" height="18" rx="1" fill="#1d4ed8"/>
      <polygon points="47,84 50,90 53,84" fill="#1d4ed8"/>
      
      {/* ===== ARMS ===== */}
      {/* Left Arm */}
      <rect x="24" y="72" width="8" height="18" rx="3" fill="url(#shirtGrad)" stroke="#2563eb" strokeWidth="1.5"/>
      {/* Left Hand */}
      <circle cx="28" cy="92" r="4" fill="#fbbf24" stroke="#eab308" strokeWidth="1"/>
      
      {/* Right Arm */}
      <rect x="68" y="72" width="8" height="18" rx="3" fill="url(#shirtGrad)" stroke="#2563eb" strokeWidth="1.5"/>
      {/* Right Hand */}
      <circle cx="72" cy="92" r="4" fill="#fbbf24" stroke="#eab308" strokeWidth="1"/>
      
      {/* ===== BADGE ===== */}
      <rect x="38" y="96" width="24" height="10" rx="4" fill="#2563eb" stroke="#1d4ed8" strokeWidth="1"/>
      <text x="50" y="104" fontSize="7" fontWeight="bold" fill="white" textAnchor="middle" fontFamily="Arial, sans-serif">AI</text>
      
      {/* ===== GRADIENTS ===== */}
      <defs>
        <linearGradient id="lemonGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#fde047"/>
          <stop offset="40%" stopColor="#facc15"/>
          <stop offset="100%" stopColor="#eab308"/>
        </linearGradient>
        
        <linearGradient id="shirtGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#3b82f6"/>
          <stop offset="100%" stopColor="#2563eb"/>
        </linearGradient>
      </defs>
    </svg>
  );
};

export default LemonMascotLogo;