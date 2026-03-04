/**
 * Appointments page - view and manage appointments.
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import { Calendar, Plus, X, ChevronLeft, ChevronRight, LayoutList, CalendarDays } from "lucide-react";
import { getAppointments, createAppointment, updateAppointmentStatus } from "@/lib/api/appointments";
import { getProviders } from "@/lib/api/providers";
import { searchPatients } from "@/lib/api/patients";
import { AppointmentCalendar } from "@/components/dashboard/AppointmentCalendar";
import type { AppointmentsResponse, AppointmentCreate, AppointmentListItem } from "@/types/appointment";
import type { Provider } from "@/types/provider";
import type { PatientListItem } from "@/types/patient";

const STATUS_TABS = [
  { value: "", label: "All" },
  { value: "scheduled", label: "Scheduled" },
  { value: "confirmed", label: "Confirmed" },
  { value: "completed", label: "Completed" },
  { value: "cancelled", label: "Cancelled" },
];

const STATUS_COLORS: Record<string, string> = {
  scheduled: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  confirmed: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  checked_in: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  in_progress: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  completed: "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-400",
  cancelled: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  no_show: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
};

function formatTime(isoString: string): string {
  return new Date(isoString).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatDate(isoString: string): string {
  return new Date(isoString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function AppointmentsPage() {
  const [data, setData] = useState<AppointmentsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("");
  const [providerFilter, setProviderFilter] = useState("");
  const [providers, setProviders] = useState<Provider[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [viewMode, setViewMode] = useState<"table" | "calendar">("table");
  const [calendarMonth, setCalendarMonth] = useState(() => {
    const now = new Date();
    return { year: now.getFullYear(), month: now.getMonth() };
  });
  const [calendarAppointments, setCalendarAppointments] = useState<AppointmentListItem[]>([]);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  const fetchAppointments = useCallback(async () => {
    try {
      setLoading(true);
      const result = await getAppointments({
        page,
        limit: 20,
        status: statusFilter || undefined,
        provider_id: providerFilter || undefined,
      });
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load appointments");
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter, providerFilter]);

  const fetchCalendarAppointments = useCallback(async () => {
    const start = new Date(calendarMonth.year, calendarMonth.month, 1);
    const end = new Date(calendarMonth.year, calendarMonth.month + 1, 0);
    try {
      const result = await getAppointments({
        start_date: start.toISOString().split("T")[0],
        end_date: end.toISOString().split("T")[0],
        limit: 500,
        status: statusFilter || undefined,
        provider_id: providerFilter || undefined,
      });
      setCalendarAppointments(result.items);
    } catch {
      // Silently fail - table view still works
    }
  }, [calendarMonth, statusFilter, providerFilter]);

  useEffect(() => {
    fetchAppointments();
  }, [fetchAppointments]);

  useEffect(() => {
    if (viewMode === "calendar") {
      fetchCalendarAppointments();
    }
  }, [viewMode, fetchCalendarAppointments]);

  useEffect(() => {
    getProviders().then(setProviders).catch(() => {});
  }, []);

  const handleStatusChange = async (id: string, newStatus: string) => {
    try {
      await updateAppointmentStatus(id, newStatus);
      fetchAppointments();
      if (viewMode === "calendar") fetchCalendarAppointments();
    } catch {
      alert("Failed to update status");
    }
  };

  const totalPages = data ? Math.ceil(data.total / data.limit) : 0;

  const selectedDayAppointments = selectedDate
    ? calendarAppointments.filter((a) => {
        const d = new Date(a.start_time);
        return (
          d.getFullYear() === selectedDate.getFullYear() &&
          d.getMonth() === selectedDate.getMonth() &&
          d.getDate() === selectedDate.getDate()
        );
      })
    : [];

  return (
    <div className="max-w-7xl">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-nunito font-bold text-zinc-900 dark:text-white flex items-center gap-3">
            <Calendar className="w-8 h-8 text-teal-600" />
            Appointments
          </h1>
          <p className="text-zinc-600 dark:text-zinc-400 mt-1">
            {data ? `${data.total} appointment${data.total !== 1 ? "s" : ""}` : "Loading..."}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* View toggle */}
          <div className="flex bg-zinc-100 dark:bg-zinc-800 rounded-lg p-0.5">
            <button
              onClick={() => setViewMode("table")}
              className={`p-2 rounded-md transition-colors ${
                viewMode === "table"
                  ? "bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white shadow-sm"
                  : "text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-300"
              }`}
              title="Table view"
            >
              <LayoutList className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode("calendar")}
              className={`p-2 rounded-md transition-colors ${
                viewMode === "calendar"
                  ? "bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white shadow-sm"
                  : "text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-300"
              }`}
              title="Calendar view"
            >
              <CalendarDays className="w-4 h-4" />
            </button>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium"
          >
            <Plus className="w-4 h-4" />
            New Appointment
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-6 flex-wrap">
        <div className="flex bg-zinc-100 dark:bg-zinc-800 rounded-lg p-0.5">
          {STATUS_TABS.map((tab) => (
            <button
              key={tab.value}
              onClick={() => { setStatusFilter(tab.value); setPage(1); }}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                statusFilter === tab.value
                  ? "bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white shadow-sm"
                  : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-800 dark:hover:text-zinc-200"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <select
          value={providerFilter}
          onChange={(e) => { setProviderFilter(e.target.value); setPage(1); }}
          className="px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg text-sm bg-white dark:bg-[#1E2530] dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
        >
          <option value="">All Providers</option>
          {providers.map((p) => (
            <option key={p.id} value={p.id}>{p.full_name}</option>
          ))}
        </select>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg mb-4 text-sm">{error}</div>
      )}

      {viewMode === "table" ? (
        <>
          {/* Table */}
          <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 shadow-sm overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-[#232A35]">
                  <th className="text-left px-4 py-3 text-xs font-semibold text-zinc-600 dark:text-zinc-400 uppercase tracking-wide">Date & Time</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-zinc-600 dark:text-zinc-400 uppercase tracking-wide">Patient</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-zinc-600 dark:text-zinc-400 uppercase tracking-wide">Provider</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-zinc-600 dark:text-zinc-400 uppercase tracking-wide">Type</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-zinc-600 dark:text-zinc-400 uppercase tracking-wide">Status</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-zinc-600 dark:text-zinc-400 uppercase tracking-wide">Reason</th>
                  <th className="text-right px-4 py-3 text-xs font-semibold text-zinc-600 dark:text-zinc-400 uppercase tracking-wide">Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading && !data ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <tr key={i} className="border-b border-zinc-100 dark:border-zinc-700 animate-pulse">
                      {Array.from({ length: 7 }).map((_, j) => (
                        <td key={j} className="px-4 py-3"><div className="h-4 bg-zinc-200 dark:bg-zinc-700 rounded w-20" /></td>
                      ))}
                    </tr>
                  ))
                ) : data?.items.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-12 text-center text-zinc-500 dark:text-zinc-400">
                      <Calendar className="w-12 h-12 text-zinc-300 dark:text-zinc-600 mx-auto mb-3" />
                      <p className="font-medium">No appointments found</p>
                      <p className="text-sm mt-1">
                        {statusFilter ? "Try a different filter" : "Create your first appointment"}
                      </p>
                    </td>
                  </tr>
                ) : (
                  data?.items.map((appt) => (
                    <tr key={appt.id} className="border-b border-zinc-100 dark:border-zinc-700 hover:bg-zinc-50 dark:hover:bg-[#252D3A] transition-colors">
                      <td className="px-4 py-3">
                        <div className="text-sm font-medium text-zinc-900 dark:text-zinc-200">{formatDate(appt.start_time)}</div>
                        <div className="text-xs text-zinc-500 dark:text-zinc-400">{formatTime(appt.start_time)} - {formatTime(appt.end_time)}</div>
                      </td>
                      <td className="px-4 py-3 text-sm text-zinc-700 dark:text-zinc-300">{appt.patient_name || "-"}</td>
                      <td className="px-4 py-3 text-sm text-zinc-700 dark:text-zinc-300">{appt.provider_name || "-"}</td>
                      <td className="px-4 py-3">
                        <span className="text-sm text-zinc-600 dark:text-zinc-400 capitalize">{appt.appointment_type.replace("_", " ")}</span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium capitalize ${
                          STATUS_COLORS[appt.status] || "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-400"
                        }`}>
                          {appt.status.replace("_", " ")}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-zinc-600 dark:text-zinc-400 max-w-[200px] truncate">{appt.reason || "-"}</td>
                      <td className="px-4 py-3 text-right">
                        {appt.status === "scheduled" && (
                          <div className="flex gap-2 justify-end">
                            <button
                              onClick={() => handleStatusChange(appt.id, "confirmed")}
                              className="text-xs text-green-600 hover:text-green-800 font-medium"
                            >
                              Confirm
                            </button>
                            <button
                              onClick={() => handleStatusChange(appt.id, "cancelled")}
                              className="text-xs text-red-600 hover:text-red-800 font-medium"
                            >
                              Cancel
                            </button>
                          </div>
                        )}
                        {appt.status === "confirmed" && (
                          <button
                            onClick={() => handleStatusChange(appt.id, "completed")}
                            className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                          >
                            Complete
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>

            {totalPages > 1 && (
              <div className="flex items-center justify-between px-4 py-3 border-t border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-[#232A35]">
                <p className="text-sm text-zinc-600 dark:text-zinc-400">Page {page} of {totalPages}</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page <= 1}
                    className="p-1.5 rounded border border-zinc-300 dark:border-zinc-600 hover:bg-white dark:hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronLeft className="w-4 h-4 dark:text-zinc-400" />
                  </button>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page >= totalPages}
                    className="p-1.5 rounded border border-zinc-300 dark:border-zinc-600 hover:bg-white dark:hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronRight className="w-4 h-4 dark:text-zinc-400" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </>
      ) : (
        /* Calendar view */
        <div className="space-y-6">
          <AppointmentCalendar
            appointments={calendarAppointments}
            month={calendarMonth.month}
            year={calendarMonth.year}
            selectedDate={selectedDate}
            onSelectDate={setSelectedDate}
            onMonthChange={(month, year) => setCalendarMonth({ month, year })}
          />

          {/* Selected day detail */}
          {selectedDate && (
            <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 shadow-sm overflow-hidden">
              <div className="p-4 border-b border-zinc-200 dark:border-zinc-700">
                <h3 className="font-semibold text-zinc-900 dark:text-white">
                  {selectedDate.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}
                </h3>
                <p className="text-sm text-zinc-500 dark:text-zinc-400">
                  {selectedDayAppointments.length} appointment{selectedDayAppointments.length !== 1 ? "s" : ""}
                </p>
              </div>
              {selectedDayAppointments.length === 0 ? (
                <div className="p-8 text-center text-zinc-500 dark:text-zinc-400 text-sm">
                  No appointments on this day
                </div>
              ) : (
                <div className="divide-y divide-zinc-100 dark:divide-zinc-700">
                  {selectedDayAppointments
                    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
                    .map((appt) => (
                      <div key={appt.id} className="p-4 flex items-center justify-between hover:bg-zinc-50 dark:hover:bg-[#252D3A] transition-colors">
                        <div className="flex items-center gap-4">
                          <div className="text-sm font-medium text-zinc-900 dark:text-zinc-200 w-28">
                            {formatTime(appt.start_time)} - {formatTime(appt.end_time)}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-zinc-900 dark:text-zinc-200">{appt.patient_name || "No patient"}</p>
                            <p className="text-xs text-zinc-500 dark:text-zinc-400 capitalize">{appt.appointment_type.replace("_", " ")}{appt.provider_name ? ` \u2022 ${appt.provider_name}` : ""}</p>
                          </div>
                        </div>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium capitalize ${
                          STATUS_COLORS[appt.status] || "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-400"
                        }`}>
                          {appt.status.replace("_", " ")}
                        </span>
                      </div>
                    ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {showCreateModal && (
        <CreateAppointmentModal
          providers={providers}
          onClose={() => setShowCreateModal(false)}
          onCreated={() => { setShowCreateModal(false); fetchAppointments(); if (viewMode === "calendar") fetchCalendarAppointments(); }}
        />
      )}
    </div>
  );
}

function CreateAppointmentModal({
  providers,
  onClose,
  onCreated,
}: {
  providers: Provider[];
  onClose: () => void;
  onCreated: () => void;
}) {
  const [saving, setSaving] = useState(false);
  const [patientSearch, setPatientSearch] = useState("");
  const [patientResults, setPatientResults] = useState<PatientListItem[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<PatientListItem | null>(null);
  const [form, setForm] = useState({
    date: "",
    start_time: "",
    end_time: "",
    provider_id: "",
    appointment_type: "checkup",
    reason: "",
  });

  useEffect(() => {
    if (patientSearch.length < 2) {
      setPatientResults([]);
      return;
    }
    const timer = setTimeout(() => {
      searchPatients(patientSearch).then(setPatientResults).catch(() => {});
    }, 300);
    return () => clearTimeout(timer);
  }, [patientSearch]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.date || !form.start_time || !form.end_time) return;

    setSaving(true);
    try {
      const data: AppointmentCreate = {
        start_time: `${form.date}T${form.start_time}:00`,
        end_time: `${form.date}T${form.end_time}:00`,
        appointment_type: form.appointment_type,
        patient_id: selectedPatient?.id,
        provider_id: form.provider_id || undefined,
        reason: form.reason || undefined,
      };
      await createAppointment(data);
      onCreated();
    } catch {
      alert("Failed to create appointment");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-[#1E2530] rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-zinc-200 dark:border-zinc-700">
          <h2 className="text-lg font-bold text-zinc-900 dark:text-white">New Appointment</h2>
          <button onClick={onClose} className="text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300">
            <X className="w-5 h-5" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Patient search */}
          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Patient</label>
            {selectedPatient ? (
              <div className="flex items-center justify-between px-3 py-2 bg-teal-50 dark:bg-teal-900/20 border border-teal-200 dark:border-teal-800 rounded-lg">
                <span className="text-sm font-medium text-teal-800 dark:text-teal-300">
                  {selectedPatient.name} ({selectedPatient.owner_first_name} {selectedPatient.owner_last_name})
                </span>
                <button type="button" onClick={() => { setSelectedPatient(null); setPatientSearch(""); }}>
                  <X className="w-4 h-4 text-teal-600 dark:text-teal-400" />
                </button>
              </div>
            ) : (
              <div className="relative">
                <input
                  placeholder="Search patient name or owner..."
                  value={patientSearch}
                  onChange={(e) => setPatientSearch(e.target.value)}
                  className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg text-sm bg-white dark:bg-[#232A35] dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
                {patientResults.length > 0 && (
                  <div className="absolute top-full left-0 right-0 bg-white dark:bg-[#232A35] border border-zinc-200 dark:border-zinc-600 rounded-lg mt-1 shadow-lg z-10 max-h-40 overflow-y-auto">
                    {patientResults.map((p) => (
                      <button
                        key={p.id}
                        type="button"
                        onClick={() => { setSelectedPatient(p); setPatientSearch(""); setPatientResults([]); }}
                        className="w-full text-left px-3 py-2 text-sm hover:bg-zinc-50 dark:hover:bg-zinc-700 dark:text-zinc-200"
                      >
                        <span className="font-medium">{p.name}</span>
                        <span className="text-zinc-500 dark:text-zinc-400"> - {p.owner_first_name} {p.owner_last_name}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Provider</label>
            <select
              value={form.provider_id}
              onChange={(e) => setForm({ ...form, provider_id: e.target.value })}
              className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg text-sm bg-white dark:bg-[#232A35] dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="">No provider assigned</option>
              {providers.map((p) => (
                <option key={p.id} value={p.id}>{p.full_name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Date *</label>
            <input
              type="date"
              required
              value={form.date}
              onChange={(e) => setForm({ ...form, date: e.target.value })}
              className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg text-sm bg-white dark:bg-[#232A35] dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Start Time *</label>
              <input
                type="time"
                required
                value={form.start_time}
                onChange={(e) => setForm({ ...form, start_time: e.target.value })}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg text-sm bg-white dark:bg-[#232A35] dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">End Time *</label>
              <input
                type="time"
                required
                value={form.end_time}
                onChange={(e) => setForm({ ...form, end_time: e.target.value })}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg text-sm bg-white dark:bg-[#232A35] dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Type</label>
              <select
                value={form.appointment_type}
                onChange={(e) => setForm({ ...form, appointment_type: e.target.value })}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg text-sm bg-white dark:bg-[#232A35] dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                {["checkup", "vaccination", "sick_visit", "surgery", "dental", "grooming", "emergency", "follow_up", "consultation", "lab_work", "other"].map((t) => (
                  <option key={t} value={t}>{t.replace("_", " ").replace(/\b\w/g, l => l.toUpperCase())}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Reason</label>
              <input
                value={form.reason}
                onChange={(e) => setForm({ ...form, reason: e.target.value })}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg text-sm bg-white dark:bg-[#232A35] dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-zinc-600 dark:text-zinc-400 hover:text-zinc-800 dark:hover:text-zinc-200">
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-4 py-2 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 disabled:opacity-50"
            >
              {saving ? "Creating..." : "Create Appointment"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
