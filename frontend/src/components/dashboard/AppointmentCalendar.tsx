/**
 * Monthly calendar grid for appointments view.
 */

"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import type { AppointmentListItem } from "@/types/appointment";

const DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const STATUS_DOT_COLORS: Record<string, string> = {
  scheduled: "bg-blue-500",
  confirmed: "bg-green-500",
  checked_in: "bg-yellow-500",
  in_progress: "bg-purple-500",
  completed: "bg-zinc-400",
  cancelled: "bg-red-500",
  no_show: "bg-orange-500",
};

interface AppointmentCalendarProps {
  appointments: AppointmentListItem[];
  month: number;
  year: number;
  selectedDate: Date | null;
  onSelectDate: (date: Date) => void;
  onMonthChange: (month: number, year: number) => void;
}

export function AppointmentCalendar({
  appointments,
  month,
  year,
  selectedDate,
  onSelectDate,
  onMonthChange,
}: AppointmentCalendarProps) {
  const today = new Date();
  const todayStr = `${today.getFullYear()}-${today.getMonth()}-${today.getDate()}`;

  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const startOffset = firstDay.getDay();
  const daysInMonth = lastDay.getDate();

  // Group appointments by day
  const appointmentsByDay: Record<number, AppointmentListItem[]> = {};
  for (const appt of appointments) {
    const d = new Date(appt.start_time);
    if (d.getFullYear() === year && d.getMonth() === month) {
      const day = d.getDate();
      if (!appointmentsByDay[day]) appointmentsByDay[day] = [];
      appointmentsByDay[day].push(appt);
    }
  }

  const handlePrev = () => {
    if (month === 0) {
      onMonthChange(11, year - 1);
    } else {
      onMonthChange(month - 1, year);
    }
  };

  const handleNext = () => {
    if (month === 11) {
      onMonthChange(0, year + 1);
    } else {
      onMonthChange(month + 1, year);
    }
  };

  const monthName = firstDay.toLocaleString("en-US", { month: "long" });

  // Build grid cells
  const cells: Array<{ day: number | null }> = [];
  for (let i = 0; i < startOffset; i++) {
    cells.push({ day: null });
  }
  for (let d = 1; d <= daysInMonth; d++) {
    cells.push({ day: d });
  }
  // Pad to fill last row
  while (cells.length % 7 !== 0) {
    cells.push({ day: null });
  }

  return (
    <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 shadow-sm overflow-hidden">
      {/* Month navigation */}
      <div className="flex items-center justify-between p-4 border-b border-zinc-200 dark:border-zinc-700">
        <button
          onClick={handlePrev}
          className="p-1.5 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-colors"
        >
          <ChevronLeft className="w-5 h-5 text-zinc-600 dark:text-zinc-400" />
        </button>
        <h3 className="text-lg font-bold text-zinc-900 dark:text-white">
          {monthName} {year}
        </h3>
        <button
          onClick={handleNext}
          className="p-1.5 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-colors"
        >
          <ChevronRight className="w-5 h-5 text-zinc-600 dark:text-zinc-400" />
        </button>
      </div>

      {/* Day headers */}
      <div className="grid grid-cols-7 border-b border-zinc-200 dark:border-zinc-700">
        {DAY_NAMES.map((name) => (
          <div key={name} className="py-2 text-center text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase">
            {name}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7">
        {cells.map((cell, i) => {
          if (cell.day === null) {
            return (
              <div key={i} className="min-h-[90px] border-b border-r border-zinc-100 dark:border-zinc-700/50 bg-zinc-50/50 dark:bg-[#1A2029]" />
            );
          }

          const dayAppts = appointmentsByDay[cell.day] || [];
          const isToday = todayStr === `${year}-${month}-${cell.day}`;
          const isSelected =
            selectedDate &&
            selectedDate.getFullYear() === year &&
            selectedDate.getMonth() === month &&
            selectedDate.getDate() === cell.day;

          return (
            <button
              key={i}
              onClick={() => onSelectDate(new Date(year, month, cell.day!))}
              className={`min-h-[90px] p-1.5 border-b border-r border-zinc-100 dark:border-zinc-700/50 text-left transition-colors hover:bg-zinc-50 dark:hover:bg-[#252D3A] ${
                isSelected ? "bg-teal-50 dark:bg-teal-900/15 ring-2 ring-inset ring-teal-500" : ""
              }`}
            >
              <div className={`text-sm font-medium mb-1 w-7 h-7 flex items-center justify-center rounded-full ${
                isToday
                  ? "bg-teal-600 text-white"
                  : "text-zinc-700 dark:text-zinc-300"
              }`}>
                {cell.day}
              </div>
              <div className="space-y-0.5">
                {dayAppts.slice(0, 3).map((appt) => (
                  <div
                    key={appt.id}
                    className="flex items-center gap-1 px-1 py-0.5 rounded text-[10px] truncate"
                  >
                    <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${STATUS_DOT_COLORS[appt.status] || "bg-zinc-400"}`} />
                    <span className="text-zinc-600 dark:text-zinc-400 truncate">
                      {new Date(appt.start_time).toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })}
                      {appt.patient_name ? ` ${appt.patient_name}` : ""}
                    </span>
                  </div>
                ))}
                {dayAppts.length > 3 && (
                  <p className="text-[10px] text-zinc-400 dark:text-zinc-500 px-1">
                    +{dayAppts.length - 3} more
                  </p>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
