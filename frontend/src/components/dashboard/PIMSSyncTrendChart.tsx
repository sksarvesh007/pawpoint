/**
 * Line chart showing PIMS sync success/failure trend over time.
 * Uses Chart.js with dual datasets for successful and failed syncs.
 */

"use client";

import { Database } from "lucide-react";
import { useMemo } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
  Legend,
  ChartOptions,
  ChartData,
} from "chart.js";
import { Line } from "react-chartjs-2";
import type { PIMSSyncDayTrend } from "@/types/analytics";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
  Legend,
);

interface PIMSSyncTrendChartProps {
  data: PIMSSyncDayTrend[];
}

export function PIMSSyncTrendChart({ data }: PIMSSyncTrendChartProps) {
  const formattedData = useMemo(() => {
    return data.map((d) => {
      const date = new Date(d.date + "T00:00:00");
      return {
        label: date.toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
        }),
        successful: d.successful,
        failed: d.failed,
      };
    });
  }, [data]);

  if (formattedData.length === 0) {
    return (
      <div className="bg-white dark:bg-[#1E2530] rounded-2xl border border-zinc-200 dark:border-zinc-700 p-6 shadow-sm">
        <h3 className="text-base font-bold text-[#1D3533] dark:text-white mb-4 flex items-center gap-2">
          <div className="p-2 bg-indigo-50 dark:bg-indigo-900/30 rounded-lg">
            <Database className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
          </div>
          PIMS Sync Trend
        </h3>
        <div className="h-48 flex items-center justify-center text-zinc-400">
          No sync data available
        </div>
      </div>
    );
  }

  const chartData: ChartData<"line"> = {
    labels: formattedData.map((d) => d.label),
    datasets: [
      {
        label: "Successful",
        data: formattedData.map((d) => d.successful),
        borderColor: "#22C55E",
        backgroundColor: (context) => {
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, 0, 0, 200);
          gradient.addColorStop(0, "rgba(34, 197, 94, 0.2)");
          gradient.addColorStop(1, "rgba(34, 197, 94, 0)");
          return gradient;
        },
        fill: true,
        tension: 0.4,
        borderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 6,
        pointBackgroundColor: "#22C55E",
        pointHoverBackgroundColor: "#22C55E",
        pointBorderColor: "#fff",
        pointHoverBorderColor: "#fff",
        pointBorderWidth: 2,
      },
      {
        label: "Failed",
        data: formattedData.map((d) => d.failed),
        borderColor: "#EF4444",
        backgroundColor: (context) => {
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, 0, 0, 200);
          gradient.addColorStop(0, "rgba(239, 68, 68, 0.2)");
          gradient.addColorStop(1, "rgba(239, 68, 68, 0)");
          return gradient;
        },
        fill: true,
        tension: 0.4,
        borderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 6,
        pointBackgroundColor: "#EF4444",
        pointHoverBackgroundColor: "#EF4444",
        pointBorderColor: "#fff",
        pointHoverBorderColor: "#fff",
        pointBorderWidth: 2,
      },
    ],
  };

  const options: ChartOptions<"line"> = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: "index",
      intersect: false,
    },
    plugins: {
      legend: {
        display: true,
        position: "top",
        align: "end",
        labels: {
          usePointStyle: true,
          pointStyle: "circle",
          padding: 16,
          font: { size: 12, weight: 500 },
          color: "#64748B",
        },
      },
      tooltip: {
        backgroundColor: "#1D3533",
        titleColor: "#fff",
        bodyColor: "#fff",
        padding: 12,
        cornerRadius: 8,
        displayColors: true,
      },
    },
    scales: {
      x: {
        grid: { display: false },
        border: { display: false },
        ticks: {
          color: "#94A3B8",
          font: { size: 11 },
          maxRotation: 0,
        },
      },
      y: {
        grid: { color: "rgba(148, 163, 184, 0.1)" },
        border: { display: false },
        ticks: {
          color: "#94A3B8",
          font: { size: 11 },
          stepSize: 1,
        },
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="bg-white dark:bg-[#1E2530] rounded-2xl border border-zinc-200 dark:border-zinc-700 p-6 shadow-sm">
      <h3 className="text-base font-bold text-[#1D3533] dark:text-white mb-4 flex items-center gap-2">
        <div className="p-2 bg-indigo-50 dark:bg-indigo-900/30 rounded-lg">
          <Database className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
        </div>
        PIMS Sync Trend
      </h3>
      <div className="h-52">
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
}
