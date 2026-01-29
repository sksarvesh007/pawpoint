/**
 * Wavy background pattern for dashboard pages.
 * Uses the same teal colors from the homepage with low opacity.
 */

import { PawBackground } from "@/components/PawBackground";

export function WaveBackground() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {/* Decorative wave - top right */}
      <svg
        className="absolute -top-20 -right-20 opacity-40"
        width="800"
        height="600"
        viewBox="0 0 800 600"
        preserveAspectRatio="none"
      >
        <path
          d="M 0,300 C 200,250 400,350 600,300 L 800,300 L 800,0 L 0,0 Z"
          fill="url(#waveGradient1)"
        />
        <defs>
          <linearGradient id="waveGradient1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#7ECDC8" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#2A9D8F" stopOpacity="0.1" />
          </linearGradient>
        </defs>
      </svg>

      {/* Decorative wave - bottom left */}
      <svg
        className="absolute -bottom-20 -left-20 opacity-30"
        width="600"
        height="400"
        viewBox="0 0 600 400"
        preserveAspectRatio="none"
      >
        <path
          d="M 0,200 C 150,150 300,250 450,200 L 600,200 L 600,400 L 0,400 Z"
          fill="url(#waveGradient2)"
        />
        <defs>
          <linearGradient id="waveGradient2" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#3EB5B0" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#7ECDC8" stopOpacity="0.1" />
          </linearGradient>
        </defs>
      </svg>

      {/* Paw print overlay - very subtle */}
      <PawBackground
        pawCount={8}
        circleCount={4}
        pawOpacity={0.04}
        circleOpacity={0.06}
        pawSizeRange={[25, 50]}
        circleSizeRange={[150, 300]}
      />
    </div>
  );
}
