/**
 * Patients page - view and manage patient records.
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import { PawPrint, Plus, Search, X, ChevronLeft, ChevronRight } from "lucide-react";
import { getPatients, createPatient, deletePatient } from "@/lib/api/patients";
import type { PatientsResponse, PatientCreate } from "@/types/patient";

const SPECIES_OPTIONS = [
  "dog", "cat", "bird", "rabbit", "hamster", "guinea_pig", "reptile", "fish", "horse", "other",
];

export default function PatientsPage() {
  const [data, setData] = useState<PatientsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [speciesFilter, setSpeciesFilter] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);

  const fetchPatients = useCallback(async () => {
    try {
      setLoading(true);
      const result = await getPatients(page, 20, search || undefined, speciesFilter || undefined);
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load patients");
    } finally {
      setLoading(false);
    }
  }, [page, search, speciesFilter]);

  useEffect(() => {
    fetchPatients();
  }, [fetchPatients]);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearch(searchInput);
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput]);

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to remove this patient?")) return;
    try {
      await deletePatient(id);
      fetchPatients();
    } catch {
      alert("Failed to delete patient");
    }
  };

  const totalPages = data ? Math.ceil(data.total / data.limit) : 0;

  return (
    <div className="max-w-7xl">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-nunito font-bold text-zinc-900 dark:text-white flex items-center gap-3">
            <PawPrint className="w-8 h-8 text-teal-600" />
            Patients
          </h1>
          <p className="text-zinc-600 dark:text-zinc-400 mt-1">
            {data ? `${data.total} patient${data.total !== 1 ? "s" : ""}` : "Loading..."}
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium"
        >
          <Plus className="w-4 h-4" />
          Add Patient
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
          <input
            type="text"
            placeholder="Search by name, owner, phone..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="w-full pl-10 pr-8 py-2.5 border border-zinc-300 dark:border-zinc-600 rounded-lg text-sm bg-white dark:bg-[#1E2530] dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
          />
          {searchInput && (
            <button
              onClick={() => setSearchInput("")}
              className="absolute right-3 top-1/2 -translate-y-1/2"
            >
              <X className="w-4 h-4 text-zinc-400" />
            </button>
          )}
        </div>
        <select
          value={speciesFilter}
          onChange={(e) => { setSpeciesFilter(e.target.value); setPage(1); }}
          className="px-3 py-2.5 border border-zinc-300 dark:border-zinc-600 rounded-lg text-sm bg-white dark:bg-[#1E2530] dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
        >
          <option value="">All Species</option>
          {SPECIES_OPTIONS.map((s) => (
            <option key={s} value={s}>{s.replace("_", " ").replace(/\b\w/g, l => l.toUpperCase())}</option>
          ))}
        </select>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg mb-4 text-sm">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 shadow-sm overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-[#232A35]">
              <th className="text-left px-4 py-3 text-xs font-semibold text-zinc-600 dark:text-zinc-400 uppercase tracking-wide">Patient</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-zinc-600 dark:text-zinc-400 uppercase tracking-wide">Species</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-zinc-600 dark:text-zinc-400 uppercase tracking-wide">Breed</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-zinc-600 dark:text-zinc-400 uppercase tracking-wide">Owner</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-zinc-600 dark:text-zinc-400 uppercase tracking-wide">Phone</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-zinc-600 dark:text-zinc-400 uppercase tracking-wide">Status</th>
              <th className="text-right px-4 py-3 text-xs font-semibold text-zinc-600 dark:text-zinc-400 uppercase tracking-wide">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && !data ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="border-b border-zinc-100 dark:border-zinc-700 animate-pulse">
                  <td className="px-4 py-3"><div className="h-4 bg-zinc-200 dark:bg-zinc-700 rounded w-24" /></td>
                  <td className="px-4 py-3"><div className="h-4 bg-zinc-200 dark:bg-zinc-700 rounded w-16" /></td>
                  <td className="px-4 py-3"><div className="h-4 bg-zinc-200 dark:bg-zinc-700 rounded w-20" /></td>
                  <td className="px-4 py-3"><div className="h-4 bg-zinc-200 dark:bg-zinc-700 rounded w-28" /></td>
                  <td className="px-4 py-3"><div className="h-4 bg-zinc-200 dark:bg-zinc-700 rounded w-24" /></td>
                  <td className="px-4 py-3"><div className="h-4 bg-zinc-200 dark:bg-zinc-700 rounded w-16" /></td>
                  <td className="px-4 py-3"><div className="h-4 bg-zinc-200 dark:bg-zinc-700 rounded w-12 ml-auto" /></td>
                </tr>
              ))
            ) : data?.items.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-12 text-center text-zinc-500 dark:text-zinc-400">
                  <PawPrint className="w-12 h-12 text-zinc-300 dark:text-zinc-600 mx-auto mb-3" />
                  <p className="font-medium">No patients found</p>
                  <p className="text-sm mt-1">
                    {search ? "Try a different search term" : "Add your first patient to get started"}
                  </p>
                </td>
              </tr>
            ) : (
              data?.items.map((patient) => (
                <tr key={patient.id} className="border-b border-zinc-100 dark:border-zinc-700 hover:bg-zinc-50 dark:hover:bg-[#252D3A] transition-colors">
                  <td className="px-4 py-3">
                    <span className="font-medium text-zinc-900 dark:text-zinc-200">{patient.name}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm text-zinc-600 dark:text-zinc-400 capitalize">{patient.species.replace("_", " ")}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm text-zinc-600 dark:text-zinc-400">{patient.breed || "-"}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm text-zinc-700 dark:text-zinc-300">{patient.owner_first_name} {patient.owner_last_name}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm text-zinc-600 dark:text-zinc-400">{patient.owner_phone}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                      patient.is_deceased
                        ? "bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400"
                        : "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                    }`}>
                      {patient.is_deceased ? "Deceased" : "Active"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleDelete(patient.id)}
                      className="text-xs text-red-600 hover:text-red-800 font-medium"
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-[#232A35]">
            <p className="text-sm text-zinc-600 dark:text-zinc-400">
              Page {page} of {totalPages}
            </p>
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

      {/* Create Modal */}
      {showCreateModal && (
        <CreatePatientModal
          onClose={() => setShowCreateModal(false)}
          onCreated={() => { setShowCreateModal(false); fetchPatients(); }}
        />
      )}
    </div>
  );
}

function CreatePatientModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<PatientCreate>({
    name: "",
    species: "dog",
    owner_first_name: "",
    owner_last_name: "",
    owner_phone: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await createPatient(form);
      onCreated();
    } catch {
      alert("Failed to create patient");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-[#1E2530] rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-zinc-200 dark:border-zinc-700">
          <h2 className="text-lg font-bold text-zinc-900 dark:text-white">Add Patient</h2>
          <button onClick={onClose} className="text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300">
            <X className="w-5 h-5" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Pet Name *</label>
            <input
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg text-sm bg-white dark:bg-[#232A35] dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Species</label>
              <select
                value={form.species}
                onChange={(e) => setForm({ ...form, species: e.target.value })}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg text-sm bg-white dark:bg-[#232A35] dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                {SPECIES_OPTIONS.map((s) => (
                  <option key={s} value={s}>{s.replace("_", " ").replace(/\b\w/g, l => l.toUpperCase())}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Breed</label>
              <input
                value={form.breed || ""}
                onChange={(e) => setForm({ ...form, breed: e.target.value || undefined })}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg text-sm bg-white dark:bg-[#232A35] dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Owner First Name *</label>
              <input
                required
                value={form.owner_first_name}
                onChange={(e) => setForm({ ...form, owner_first_name: e.target.value })}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg text-sm bg-white dark:bg-[#232A35] dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Owner Last Name *</label>
              <input
                required
                value={form.owner_last_name}
                onChange={(e) => setForm({ ...form, owner_last_name: e.target.value })}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg text-sm bg-white dark:bg-[#232A35] dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Phone *</label>
              <input
                required
                value={form.owner_phone}
                onChange={(e) => setForm({ ...form, owner_phone: e.target.value })}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg text-sm bg-white dark:bg-[#232A35] dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Email</label>
              <input
                type="email"
                value={form.owner_email || ""}
                onChange={(e) => setForm({ ...form, owner_email: e.target.value || undefined })}
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
              {saving ? "Creating..." : "Create Patient"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
