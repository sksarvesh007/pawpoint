/**
 * Horizontal bar chart showing appointment status breakdown.
 * Uses Chart.js Bar chart with appointments_by_status data.
 */

"use client";

import { Calendar } from "lucide-react";
import { useMemo } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
  ChartData,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
);

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  scheduled: { label: "Scheduled", color: "#3B82F6" },
  confirmed: { label: "Confirmed", color: "#0D9488" },
  completed: { label: "Completed", color: "#22C55E" },
  cancelled: { label: "Cancelled", color: "#EF4444" },
  no_show: { label: "No Show", color: "#F59E0B" },
  requested: { label: "Requested", color: "#8B5CF6" },
  checked_in: { label: "Checked In", color: "#06B6D4" },
  in_progress: { label: "In Progress", color: "#6366F1" },
  rescheduled: { label: "Rescheduled", color: "#EC4899" },
};

interface AppointmentStatusChartProps {
  data: Record<string, number>;
}

export function AppointmentStatusChart({ data }: AppointmentStatusChartProps) {
  const { labels, values, colors } = useMemo(() => {
    const entries = Object.entries(data)
      .filter(([, count]) => count > 0)
      .sort((a, b) => b[1] - a[1]);

    return {
      labels: entries.map(
        ([status]) => STATUS_CONFIG[status]?.label || status,
      ),
      values: entries.map(([, count]) => count),
      colors: entries.map(
        ([status]) => STATUS_CONFIG[status]?.color || "#94A3B8",
      ),
    };
  }, [data]);

  if (labels.length === 0) {
    return (
      <div className="bg-white dark:bg-[#1E2530] rounded-2xl border border-zinc-200 dark:border-zinc-700 p-6 shadow-sm">
        <h3 className="text-base font-bold text-[#1D3533] dark:text-white mb-4 flex items-center gap-2">
          <div className="p-2 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
            <Calendar className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          Appointment Status
        </h3>
        <div className="h-48 flex items-center justify-center text-zinc-400">
          No appointment data
        </div>
      </div>
    );
  }

  const chartData: ChartData<"bar"> = {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor: colors,
        borderRadius: 6,
        barThickness: 24,
      },
    ],
  };

  const options: ChartOptions<"bar"> = {
    indexAxis: "y",
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#1D3533",
        titleColor: "#fff",
        bodyColor: "#fff",
        padding: 12,
        cornerRadius: 8,
        callbacks: {
          label: (context) => ` ${context.parsed.x} appointments`,
        },
      },
    },
    scales: {
      x: {
        grid: { color: "rgba(148, 163, 184, 0.1)" },
        border: { display: false },
        ticks: {
          color: "#94A3B8",
          font: { size: 11 },
          stepSize: 1,
        },
        beginAtZero: true,
      },
      y: {
        grid: { display: false },
        border: { display: false },
        ticks: {
          color: "#64748B",
          font: { size: 12, weight: 500 },
        },
      },
    },
  };

  return (
    <div className="bg-white dark:bg-[#1E2530] rounded-2xl border border-zinc-200 dark:border-zinc-700 p-6 shadow-sm">
      <h3 className="text-base font-bold text-[#1D3533] dark:text-white mb-4 flex items-center gap-2">
        <div className="p-2 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
          <Calendar className="w-5 h-5 text-blue-600 dark:text-blue-400" />
        </div>
        Appointment Status
      </h3>
      <div style={{ height: Math.max(labels.length * 40 + 20, 120) }}>
        <Bar data={chartData} options={options} />
      </div>
    </div>
  );
}
