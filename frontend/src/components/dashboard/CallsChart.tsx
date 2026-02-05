/**
 * Traffic chart showing 24-hour call and chat distribution.
 * Uses Chart.js for smooth, professional visualization.
 * Chat data is optional - shows zeros until actual data is available.
 * Data comes from backend in UTC - converted to local timezone for display.
 */

"use client";

import { Activity } from "lucide-react";
import { useRef, useMemo } from "react";
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
  chatData?: Array<{ hour: number; count: number }>;
  emergencyTransfers?: number;
  transferHours?: number[]; // UTC hours when transfers occurred
}

/**
 * Convert UTC hour to local hour based on browser timezone.
 */
function utcToLocalHour(utcHour: number): number {
  // getTimezoneOffset returns minutes, negative for east of UTC
  const offsetMinutes = new Date().getTimezoneOffset();
  const offsetHours = -offsetMinutes / 60; // Convert to positive hours for east
  return (utcHour + offsetHours + 24) % 24;
}

/**
 * Convert local hour to UTC hour.
 */
function localToUtcHour(localHour: number): number {
  const offsetMinutes = new Date().getTimezoneOffset();
  const offsetHours = -offsetMinutes / 60;
  return (localHour - offsetHours + 24) % 24;
}

/**
 * Rotate hourly data from UTC to local timezone order.
 * Data comes indexed by UTC hour (0-23), we reorder to local hours.
 */
function convertToLocalTimezone(
  utcData: Array<{ hour: number; count: number }>,
): Array<{ hour: number; count: number }> {
  // Create a map of UTC hour -> count
  const utcMap = new Map(utcData.map((d) => [d.hour, d.count]));

  // Build array in local hour order (0-23)
  return Array.from({ length: 24 }, (_, localHour) => {
    const utcHour = Math.floor(localToUtcHour(localHour));
    return {
      hour: localHour,
      count: utcMap.get(utcHour) || 0,
    };
  });
}

/**
 * Convert UTC transfer hours to local hours.
 */
function convertTransferHoursToLocal(utcHours: number[]): number[] {
  return utcHours.map((h) => Math.floor(utcToLocalHour(h)));
}

export function CallsChart({
  data,
  chatData,
  emergencyTransfers = 0,
  transferHours = [],
}: CallsChartProps) {
  const chartRef = useRef<ChartJS<"line">>(null);

  // Convert data from UTC to local timezone
  const localData = useMemo(() => convertToLocalTimezone(data || []), [data]);
  const localChatData = useMemo(
    () => (chatData ? convertToLocalTimezone(chatData) : null),
    [chatData],
  );
  const localTransferHours = useMemo(
    () => convertTransferHoursToLocal(transferHours),
    [transferHours],
  );

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

  const labels = localData.map((item) =>
    item.hour % 4 === 0 ? `${item.hour}:00` : "",
  );

  const callsPointRadius = localData.map((item) =>
    localTransferHours.includes(item.hour) ? 8 : 0,
  );

  const callsPointBackgroundColor = localData.map((item) =>
    localTransferHours.includes(item.hour) ? "#E11D48" : "transparent",
  );

  // Use provided chat data or default to zeros
  const chatsDataPoints = localChatData
    ? localChatData.map((item) => item.count)
    : localData.map(() => 0);

  const chartDataConfig: ChartData<"line"> = {
    labels,
    datasets: [
      {
        label: "Calls",
        data: localData.map((item) => item.count),
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
        data: chatsDataPoints,
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
            const hour = localData[items[0].dataIndex]?.hour;
            return `${hour}:00`;
          },
          label: (context) => {
            const label = context.dataset.label || "";
            const value = context.parsed.y;
            return ` ${label}: ${value}`;
          },
          afterBody: (items) => {
            const hour = localData[items[0].dataIndex]?.hour;
            if (localTransferHours.includes(hour) && emergencyTransfers > 0) {
              return [`\n⚠️ Transfer occurred at this hour`];
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
          stepSize: 1,
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
        {localTransferHours.length > 0 && (
          <div className="flex items-center gap-2 text-xs text-zinc-500">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-rose-500"></span>
              Transfer point
            </span>
          </div>
        )}
      </div>

      <div className="h-72">
        <Line ref={chartRef} data={chartDataConfig} options={options} />
      </div>
    </div>
  );
}
