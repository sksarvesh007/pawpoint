/**
 * Reusable stats card component for dashboard metrics.
 * Matches the reference design with cream background and colored icons.
 */

import type { LucideIcon } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string | number | undefined;
  subtitle?: string;
  icon: LucideIcon;
  trend?: string;
  trendUp?: boolean;
  color?: "orange" | "teal" | "blue" | "green" | "purple";
}

export function StatsCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendUp,
  color = "teal",
}: StatsCardProps) {
  const colorClasses = {
    orange: {
      bg: "bg-[#F4A261]",
      text: "text-[#F4A261]",
    },
    teal: {
      bg: "bg-[#3EB5B0]",
      text: "text-[#3EB5B0]",
    },
    blue: {
      bg: "bg-[#4A90E2]",
      text: "text-[#4A90E2]",
    },
    green: {
      bg: "bg-[#50C878]",
      text: "text-[#50C878]",
    },
    purple: {
      bg: "bg-[#9B59B6]",
      text: "text-[#9B59B6]",
    },
  };

  const colors = colorClasses[color];

  return (
    <div className="bg-[#FFF9F0] rounded-2xl border border-orange-100/50 p-6 shadow-sm hover:shadow-md transition-all hover:-translate-y-1">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-[#5C6F6C] font-semibold">{title}</p>
          <p className="text-4xl font-black text-[#1D3533] mt-3 font-nunito">
            {value !== undefined && value !== null ? value : "—"}
          </p>
          {subtitle && (
            <p className="text-sm text-[#F4A261] mt-2 font-bold">{subtitle}</p>
          )}
        </div>
        <div className={`p-3 ${colors.bg} rounded-xl shrink-0 shadow-sm`}>
          <Icon className="w-7 h-7 text-white" />
        </div>
      </div>
      {trend && (
        <div
          className={`mt-4 flex items-center text-sm font-bold ${
            trendUp ? "text-green-600" : "text-red-600"
          }`}
        >
          <span className="mr-1">{trendUp ? "↑" : "↓"}</span>
          <span>{trend} last 7 days</span>
        </div>
      )}
    </div>
  );
}
