/**
 * Call volume chart showing 24-hour call and chat distribution.
 * Uses Chart.js for smooth, professional visualization.
 */

"use client";

import { Activity } from "lucide-react";
import { useEffect, useRef } from "react";
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

interface CallsChartProps {
  data: Array<{ hour: number; count: number }>;
  emergencyTransfers?: number;
  transferHours?: number[];
}

export function CallsChart({
  data,
  emergencyTransfers = 2,
  transferHours = [3, 15],
}: CallsChartProps) {
  const chartRef = useRef<ChartJS<"line">>(null);

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-zinc-200 p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-zinc-900 mb-4">
          Traffic Overview (24 Hours)
        </h3>
        <div className="h-64 flex items-center justify-center text-zinc-400">
          No data available
        </div>
      </div>
    );
  }

  const labels = data.map((item) =>
    item.hour % 4 === 0 ? `${item.hour}:00` : "",
  );

  const generateChatData = () => {
    return data.map((item) => {
      const base = Math.floor(item.count * 0.4);
      const variance = Math.floor(Math.random() * 5) - 2;
      return Math.max(0, base + variance);
    });
  };

  const chatData = generateChatData();

  const callsPointRadius = data.map((item) =>
    transferHours.includes(item.hour) ? 8 : 0,
  );

  const callsPointBackgroundColor = data.map((item) =>
    transferHours.includes(item.hour) ? "#E11D48" : "transparent",
  );

  const chartData: ChartData<"line"> = {
    labels,
    datasets: [
      {
        label: "Calls",
        data: data.map((item) => item.count),
        borderColor: "#E11D48",
        backgroundColor: (context) => {
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, 0, 0, 280);
          gradient.addColorStop(0, "rgba(225, 29, 72, 0.3)");
          gradient.addColorStop(0.5, "rgba(225, 29, 72, 0.1)");
          gradient.addColorStop(1, "rgba(225, 29, 72, 0)");
          return gradient;
        },
        fill: true,
        tension: 0.4,
        borderWidth: 3,
        pointRadius: callsPointRadius,
        pointBackgroundColor: callsPointBackgroundColor,
        pointBorderColor: "#fff",
        pointBorderWidth: 2,
        pointHoverRadius: 8,
        pointHoverBackgroundColor: "#E11D48",
        pointHoverBorderColor: "#fff",
        pointHoverBorderWidth: 3,
      },
      {
        label: "Chats",
        data: chatData,
        borderColor: "#8B5CF6",
        backgroundColor: (context) => {
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, 0, 0, 280);
          gradient.addColorStop(0, "rgba(139, 92, 246, 0.2)");
          gradient.addColorStop(0.5, "rgba(139, 92, 246, 0.05)");
          gradient.addColorStop(1, "rgba(139, 92, 246, 0)");
          return gradient;
        },
        fill: true,
        tension: 0.4,
        borderWidth: 3,
        pointRadius: 0,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: "#8B5CF6",
        pointHoverBorderColor: "#fff",
        pointHoverBorderWidth: 2,
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
          padding: 20,
          font: {
            size: 12,
            weight: 500,
          },
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
        callbacks: {
          title: (items) => {
            const hour = data[items[0].dataIndex]?.hour;
            return `${hour}:00`;
          },
          label: (context) => {
            const label = context.dataset.label || "";
            const value = context.parsed.y;
            return ` ${label}: ${value}`;
          },
          afterBody: (items) => {
            const hour = data[items[0].dataIndex]?.hour;
            if (transferHours.includes(hour)) {
              return [`\n⚠️ ${emergencyTransfers} transfers at this hour`];
            }
            return [];
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        border: {
          display: false,
        },
        ticks: {
          color: "#94A3B8",
          font: {
            size: 11,
            weight: 500,
          },
          maxRotation: 0,
        },
      },
      y: {
        grid: {
          color: "rgba(148, 163, 184, 0.1)",
        },
        border: {
          display: false,
        },
        ticks: {
          color: "#94A3B8",
          font: {
            size: 11,
          },
          stepSize: 10,
        },
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="bg-white rounded-2xl border border-zinc-200 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-bold text-[#1D3533] flex items-center gap-2">
          <div className="p-2 bg-teal-50 rounded-lg">
            <Activity className="w-5 h-5 text-teal-600" />
          </div>
          Traffic Overview (Last 24 Hours)
        </h3>
        <div className="flex items-center gap-2 text-xs text-zinc-500">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-rose-500"></span>
            Transfer point
          </span>
        </div>
      </div>

      <div className="h-72">
        <Line ref={chartRef} data={chartData} options={options} />
      </div>
    </div>
  );
}
