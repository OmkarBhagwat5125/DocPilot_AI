import React from 'react';

const Logo = ({ size = 32, className = '' }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        <linearGradient id="logo-gradient" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
          <stop stopColor="#6366f1" />
          <stop offset="1" stopColor="#a855f7" />
        </linearGradient>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="1.5" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>
      
      <g filter="url(#glow)">
        <path
          d="M16 2.667L29.333 13.333L16 29.333L2.667 13.333L16 2.667Z"
          fill="url(#logo-gradient)"
          opacity="0.9"
        />
        <path
          d="M16 2.667L29.333 13.333L16 21.333L2.667 13.333L16 2.667Z"
          fill="#ffffff"
          opacity="0.3"
        />
        <path
          d="M16 21.333V29.333M2.667 13.333L16 13.333H29.333"
          stroke="#ffffff"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        
        {/* Sparkle/circuit accents */}
        <circle cx="24" cy="8" r="1.5" fill="#ffffff" />
        <path d="M24 4V6M28 8H26M24 12V10M20 8H22" stroke="#ffffff" strokeWidth="1" strokeLinecap="round" />
      </g>
    </svg>
  );
};

export default Logo;
