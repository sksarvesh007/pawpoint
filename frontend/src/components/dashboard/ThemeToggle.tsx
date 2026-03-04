"use client";

import { useTheme } from "next-themes";
import { Sun, Moon } from "lucide-react";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <button
        className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all bg-white/40 dark:bg-white/10 backdrop-blur-sm border border-white/50 dark:border-white/10"
        aria-label="Toggle theme"
      >
        <div className="p-2 rounded-xl shrink-0 bg-gradient-to-br from-amber-400 to-orange-400 text-white shadow-sm">
          <Sun className="w-4 h-4" strokeWidth={2.5} />
        </div>
        <span className="text-[13px] font-medium text-[#1D3533]/70 dark:text-zinc-400">
          Light Mode
        </span>
      </button>
    );
  }

  const isDark = theme === "dark";

  return (
    <button
      onClick={() => setTheme(isDark ? "light" : "dark")}
      className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all bg-white/40 dark:bg-white/10 hover:bg-white/60 dark:hover:bg-white/15 backdrop-blur-sm border border-white/50 dark:border-white/10 group"
      aria-label="Toggle theme"
    >
      <div
        className={`p-2 rounded-xl shrink-0 shadow-sm transition-all ${
          isDark
            ? "bg-gradient-to-br from-indigo-500 to-purple-600 text-white"
            : "bg-gradient-to-br from-amber-400 to-orange-400 text-white"
        }`}
      >
        {isDark ? (
          <Moon className="w-4 h-4" strokeWidth={2.5} />
        ) : (
          <Sun className="w-4 h-4" strokeWidth={2.5} />
        )}
      </div>
      <span className="text-[13px] font-medium text-[#1D3533]/70 dark:text-zinc-400 group-hover:text-[#1D3533] dark:group-hover:text-zinc-200">
        {isDark ? "Dark Mode" : "Light Mode"}
      </span>
    </button>
  );
}
