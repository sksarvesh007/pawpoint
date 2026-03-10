/**
 * Reports page - Generate, view, and export clinic reports.
 */

"use client";

import { useState, useEffect } from "react";
import {
  BarChart3,
  Download,
  Loader2,
  X,
  FileText,
  Phone,
  Calendar,
  Users,
  Bot,
} from "lucide-react";
import { generateReport, getExportUrl } from "@/lib/api/reports";
import type { ReportResponse } from "@/types/reports";

const REPORT_TYPES = [
  {
    value: "call_summary",
    label: "Call Summary",
    description: "Daily call volume, duration, and outcomes",
    icon: Phone,
  },
  {
    value: "appointment_summary",
    label: "Appointments",
    description: "Appointment status breakdown by day",
    icon: Calendar,
  },
  {
    value: "patient_summary",
    label: "Patients",
    description: "Patient count by species with new registrations",
    icon: Users,
  },
  {
    value: "ai_performance",
    label: "AI Performance",
    description: "Confidence scores, sentiment, and transfer rates",
    icon: Bot,
  },
];

function getDefaultDates() {
  const end = new Date();
  const start = new Date();
  start.setDate(start.getDate() - 30);
  return {
    start: start.toISOString().split("T")[0],
    end: end.toISOString().split("T")[0],
  };
}

export default function ReportsPage() {
  const defaults = getDefaultDates();
  const [selectedType, setSelectedType] = useState("call_summary");
  const [startDate, setStartDate] = useState(defaults.start);
  const [endDate, setEndDate] = useState(defaults.end);
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    handleGenerate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleGenerate = async () => {
    setError("");
    setLoading(true);
    try {
      const data = await generateReport(selectedType, startDate, endDate);
      setReport(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to generate report"
      );
      setReport(null);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    const url = getExportUrl(selectedType, startDate, endDate);
    window.open(url, "_blank");
  };

  return (
    <div className="max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-nunito font-bold text-zinc-900 flex items-center gap-3">
          <BarChart3 className="w-8 h-8 text-teal-600" />
          Reports
        </h1>
        <p className="text-zinc-600 mt-1">
          Generate and export clinic reports with custom date ranges
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-lg bg-red-50 p-4 text-sm text-red-600 flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError("")}>
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Report Type Selector */}
      <div className="bg-white rounded-xl border border-zinc-200 p-6 shadow-sm mb-6">
        <h2 className="text-lg font-bold text-zinc-900 mb-4">Report Type</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {REPORT_TYPES.map((rt) => {
            const Icon = rt.icon;
            return (
              <button
                key={rt.value}
                onClick={() => setSelectedType(rt.value)}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  selectedType === rt.value
                    ? "border-teal-500 bg-teal-50"
                    : "border-zinc-200 hover:border-zinc-300 cursor-pointer"
                }`}
              >
                <Icon
                  className={`w-5 h-5 mb-2 ${
                    selectedType === rt.value
                      ? "text-teal-600"
                      : "text-zinc-400"
                  }`}
                />
                <p className="font-semibold text-zinc-900 text-sm">
                  {rt.label}
                </p>
                <p className="text-xs text-zinc-500 mt-0.5">
                  {rt.description}
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Date Range & Actions */}
      <div className="bg-white rounded-xl border border-zinc-200 p-6 shadow-sm mb-6">
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">
              Start Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="px-3 py-2 border border-zinc-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">
              End Date
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="px-3 py-2 border border-zinc-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 disabled:opacity-50"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <FileText className="w-4 h-4" />
            )}
            Generate
          </button>
          {report && (
            <button
              onClick={handleExport}
              className="flex items-center gap-2 px-5 py-2 border border-zinc-300 text-zinc-700 rounded-lg text-sm font-medium hover:bg-zinc-50"
            >
              <Download className="w-4 h-4" />
              Export CSV
            </button>
          )}
        </div>
      </div>

      {/* Report Results */}
      {loading && (
        <div className="bg-white rounded-xl border border-zinc-200 p-12 shadow-sm text-center">
          <Loader2 className="w-8 h-8 animate-spin text-teal-600 mx-auto mb-3" />
          <p className="text-zinc-500 text-sm">Generating report...</p>
        </div>
      )}

      {report && !loading && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            {Object.entries(report.summary).map(([key, value]) => (
              <div
                key={key}
                className="bg-white rounded-xl border border-zinc-200 p-4 shadow-sm"
              >
                <p className="text-xs text-zinc-500 capitalize">
                  {key.replace(/_/g, " ")}
                </p>
                <p className="text-2xl font-bold text-zinc-900 mt-1">
                  {typeof value === "number" && value % 1 !== 0
                    ? value.toFixed(1)
                    : value}
                  {key.includes("rate") || key.includes("percentage")
                    ? "%"
                    : ""}
                </p>
              </div>
            ))}
          </div>

          {/* Data Table */}
          <div className="bg-white rounded-xl border border-zinc-200 shadow-sm overflow-hidden">
            <div className="p-6 pb-4 flex items-center justify-between">
              <h2 className="text-lg font-bold text-zinc-900">
                {report.title}
              </h2>
              <p className="text-xs text-zinc-500">
                {report.start_date} to {report.end_date}
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-zinc-200 bg-zinc-50">
                    {report.columns.map((col) => (
                      <th
                        key={col}
                        className="text-left px-6 py-3 text-xs font-semibold text-zinc-600 uppercase tracking-wide whitespace-nowrap"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {report.rows.map((row, idx) => (
                    <tr
                      key={idx}
                      className="border-b border-zinc-100 hover:bg-zinc-50"
                    >
                      {Object.values(row).map((val, i) => (
                        <td
                          key={i}
                          className="px-6 py-3 text-sm text-zinc-700 whitespace-nowrap"
                        >
                          {typeof val === "number" && val % 1 !== 0
                            ? val.toFixed(1)
                            : val}
                        </td>
                      ))}
                    </tr>
                  ))}
                  {report.rows.length === 0 && (
                    <tr>
                      <td
                        colSpan={report.columns.length}
                        className="px-6 py-8 text-center text-sm text-zinc-500"
                      >
                        No data for the selected period.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
