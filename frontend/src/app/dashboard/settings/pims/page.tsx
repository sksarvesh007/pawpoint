/**
 * PIMS Integration Settings page.
 * Connect, configure, and sync with Practice Information Management Systems.
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Database,
  Plug,
  PlugZap,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Loader2,
  X,
} from "lucide-react";
import {
  getPIMSStatus,
  savePIMSCredentials,
  testPIMSConnection,
  disconnectPIMS,
  triggerSync,
  getSyncLogs,
} from "@/lib/api/pims";
import type {
  PIMSConnectionStatus,
  PIMSSyncLog,
} from "@/types/pims";

const PIMS_TYPES = [
  {
    value: "ezyvet",
    label: "ezyVet",
    description: "Cloud-based veterinary practice management",
    fields: [
      { key: "partner_id", label: "Partner ID", type: "text" },
      { key: "client_id", label: "Client ID", type: "text" },
      { key: "client_secret", label: "Client Secret", type: "password" },
    ],
  },
  {
    value: "vetspire",
    label: "Vetspire",
    description: "Modern veterinary software platform",
    fields: [
      { key: "api_key", label: "API Key", type: "password" },
      { key: "location_id", label: "Location ID (optional)", type: "text" },
    ],
  },
  {
    value: "covetrus",
    label: "Covetrus Pulse",
    description: "Comprehensive practice management (coming soon)",
    fields: [
      { key: "api_key", label: "API Key", type: "password" },
      { key: "practice_id", label: "Practice ID", type: "text" },
    ],
    disabled: true,
  },
];

const SYNC_ENTITIES = [
  { key: "patients" as const, label: "Patients", description: "Sync patient records" },
  { key: "appointments" as const, label: "Appointments", description: "Sync appointment data" },
  { key: "providers" as const, label: "Providers", description: "Sync provider/staff records" },
];

export default function PIMSSettingsPage() {
  const [status, setStatus] = useState<PIMSConnectionStatus | null>(null);
  const [syncLogs, setSyncLogs] = useState<PIMSSyncLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState("");
  const [credentials, setCredentials] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [disconnecting, setDisconnecting] = useState(false);
  const [syncingEntity, setSyncingEntity] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadStatus = useCallback(async () => {
    try {
      const [pimsStatus, logs] = await Promise.all([
        getPIMSStatus(),
        getSyncLogs(10),
      ]);
      setStatus(pimsStatus);
      setSyncLogs(logs);
      if (pimsStatus.pims_type && pimsStatus.pims_type !== "none") {
        setSelectedType(pimsStatus.pims_type);
      }
    } catch {
      setError("Failed to load PIMS status");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStatus();
  }, [loadStatus]);

  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(""), 4000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  const isConnected = status?.connection_status === "connected";

  const handleSaveCredentials = async () => {
    if (!selectedType) {
      setError("Please select a PIMS type");
      return;
    }

    const pimsConfig = PIMS_TYPES.find((p) => p.value === selectedType);
    if (!pimsConfig) return;

    const missingFields = pimsConfig.fields.filter((f) => !f.label.includes("(optional)") && !credentials[f.key]?.trim());
    if (missingFields.length > 0) {
      setError(`Please fill in: ${missingFields.map((f) => f.label).join(", ")}`);
      return;
    }

    setError("");
    setSaving(true);
    try {
      const result = await savePIMSCredentials({
        pims_type: selectedType,
        credentials,
      });
      setStatus(result);
      setSuccess("PIMS credentials saved successfully");
      setCredentials({});
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save credentials");
    } finally {
      setSaving(false);
    }
  };

  const handleTestConnection = async () => {
    setError("");
    setTesting(true);
    try {
      const result = await testPIMSConnection();
      if (result.connected) {
        setSuccess("Connection successful!");
        loadStatus();
      } else {
        setError(`Connection failed: ${result.message}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Connection test failed");
    } finally {
      setTesting(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm("Are you sure you want to disconnect from your PIMS? This will stop all syncing.")) {
      return;
    }
    setError("");
    setDisconnecting(true);
    try {
      const result = await disconnectPIMS();
      setStatus(result);
      setSelectedType("");
      setCredentials({});
      setSuccess("PIMS disconnected successfully");
      setSyncLogs([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to disconnect");
    } finally {
      setDisconnecting(false);
    }
  };

  const handleSync = async (entity: "patients" | "appointments" | "providers") => {
    setError("");
    setSyncingEntity(entity);
    try {
      await triggerSync(entity);
      setSuccess(`${entity.charAt(0).toUpperCase() + entity.slice(1)} sync started`);
      setTimeout(() => loadStatus(), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to sync ${entity}`);
    } finally {
      setSyncingEntity(null);
    }
  };

  const selectedPIMS = PIMS_TYPES.find((p) => p.value === selectedType);

  if (loading) {
    return (
      <div className="max-w-4xl">
        <div className="animate-pulse space-y-4">
          <div className="h-10 bg-zinc-200 rounded w-64" />
          <div className="h-96 bg-zinc-200 rounded-xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-nunito font-bold text-zinc-900 flex items-center gap-3">
          <Database className="w-8 h-8 text-teal-600" />
          PIMS Integration
        </h1>
        <p className="text-zinc-600 mt-1">
          Connect your Practice Information Management System to sync patients, appointments, and providers
        </p>
      </div>

      {/* Messages */}
      {error && (
        <div className="mb-6 rounded-lg bg-red-50 p-4 text-sm text-red-600 flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError("")}>
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
      {success && (
        <div className="mb-6 rounded-lg bg-green-50 p-4 text-sm text-green-600 flex items-center justify-between">
          <span>{success}</span>
          <button onClick={() => setSuccess("")}>
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Connection Status */}
      <div className="bg-white rounded-xl border border-zinc-200 p-6 shadow-sm mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-zinc-900">Connection Status</h2>
          <span
            className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold ${
              isConnected
                ? "bg-green-100 text-green-700"
                : "bg-zinc-100 text-zinc-600"
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                isConnected ? "bg-green-600 animate-pulse" : "bg-zinc-400"
              }`}
            />
            {isConnected ? "Connected" : "Not Connected"}
          </span>
        </div>

        {isConnected && status && (
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="text-center p-3 bg-zinc-50 rounded-lg">
              <p className="text-sm font-medium text-zinc-900 capitalize">{status.pims_type}</p>
              <p className="text-xs text-zinc-500">Provider</p>
            </div>
            <div className="text-center p-3 bg-zinc-50 rounded-lg">
              <p className="text-sm font-medium text-zinc-900">
                {status.last_sync_at
                  ? new Date(status.last_sync_at).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                      hour: "numeric",
                      minute: "2-digit",
                    })
                  : "Never"}
              </p>
              <p className="text-xs text-zinc-500">Last Sync</p>
            </div>
            <div className="text-center p-3 bg-zinc-50 rounded-lg">
              <p className="text-sm font-medium text-zinc-900 capitalize">
                {status.connection_status.replace(/_/g, " ")}
              </p>
              <p className="text-xs text-zinc-500">Status</p>
            </div>
          </div>
        )}

        {isConnected && (
          <div className="flex gap-3">
            <button
              onClick={handleTestConnection}
              disabled={testing}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-zinc-700 border border-zinc-300 rounded-lg hover:bg-zinc-50 disabled:opacity-50"
            >
              {testing ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <PlugZap className="w-4 h-4" />
              )}
              Test Connection
            </button>
            <button
              onClick={handleDisconnect}
              disabled={disconnecting}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 border border-red-200 rounded-lg hover:bg-red-50 disabled:opacity-50"
            >
              {disconnecting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Plug className="w-4 h-4" />
              )}
              Disconnect
            </button>
          </div>
        )}
      </div>

      {/* Connect / Configure */}
      {!isConnected && (
        <div className="bg-white rounded-xl border border-zinc-200 p-6 shadow-sm mb-6">
          <h2 className="text-lg font-bold text-zinc-900 mb-4">Connect Your PIMS</h2>

          {/* PIMS Type Selector */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-zinc-700 mb-3">
              Select your PIMS provider
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {PIMS_TYPES.map((pims) => (
                <button
                  key={pims.value}
                  type="button"
                  onClick={() => {
                    if (!pims.disabled) {
                      setSelectedType(pims.value);
                      setCredentials({});
                    }
                  }}
                  disabled={pims.disabled}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    pims.disabled
                      ? "border-zinc-100 bg-zinc-50 opacity-60 cursor-not-allowed"
                      : selectedType === pims.value
                        ? "border-teal-500 bg-teal-50"
                        : "border-zinc-200 hover:border-zinc-300 cursor-pointer"
                  }`}
                >
                  <p className="font-semibold text-zinc-900">{pims.label}</p>
                  <p className="text-xs text-zinc-500 mt-1">{pims.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Credential Fields */}
          {selectedPIMS && !selectedPIMS.disabled && (
            <div className="space-y-4">
              <h3 className="text-sm font-medium text-zinc-700">
                Enter your {selectedPIMS.label} credentials
              </h3>
              {selectedPIMS.fields.map((field) => (
                <div key={field.key}>
                  <label className="block text-sm font-medium text-zinc-600 mb-1">
                    {field.label}
                  </label>
                  <input
                    type={field.type}
                    value={credentials[field.key] || ""}
                    onChange={(e) =>
                      setCredentials({ ...credentials, [field.key]: e.target.value })
                    }
                    className="w-full px-3 py-2.5 border border-zinc-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                    placeholder={`Enter ${field.label.toLowerCase()}`}
                  />
                </div>
              ))}

              <div className="flex gap-3 pt-2">
                <button
                  onClick={handleSaveCredentials}
                  disabled={saving}
                  className="flex items-center gap-2 px-5 py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 disabled:opacity-50"
                >
                  {saving ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Plug className="w-4 h-4" />
                  )}
                  Save & Connect
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Sync Controls */}
      {isConnected && (
        <div className="bg-white rounded-xl border border-zinc-200 p-6 shadow-sm mb-6">
          <h2 className="text-lg font-bold text-zinc-900 mb-4">Sync Data</h2>
          <p className="text-sm text-zinc-500 mb-4">
            Trigger a manual sync or wait for automatic syncing (patients every 6h, appointments every 15m).
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {SYNC_ENTITIES.map((entity) => (
              <button
                key={entity.key}
                onClick={() => handleSync(entity.key)}
                disabled={syncingEntity !== null}
                className="flex items-center gap-3 p-4 border border-zinc-200 rounded-lg hover:bg-zinc-50 disabled:opacity-50 transition-colors text-left"
              >
                {syncingEntity === entity.key ? (
                  <Loader2 className="w-5 h-5 text-teal-600 animate-spin flex-shrink-0" />
                ) : (
                  <RefreshCw className="w-5 h-5 text-teal-600 flex-shrink-0" />
                )}
                <div>
                  <p className="text-sm font-medium text-zinc-900">{entity.label}</p>
                  <p className="text-xs text-zinc-500">{entity.description}</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Sync Logs */}
      {syncLogs.length > 0 && (
        <div className="bg-white rounded-xl border border-zinc-200 shadow-sm overflow-hidden">
          <div className="p-6 pb-4">
            <h2 className="text-lg font-bold text-zinc-900">Recent Sync History</h2>
          </div>
          <table className="w-full">
            <thead>
              <tr className="border-b border-zinc-200 bg-zinc-50">
                <th className="text-left px-6 py-3 text-xs font-semibold text-zinc-600 uppercase tracking-wide">
                  Entity
                </th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-zinc-600 uppercase tracking-wide">
                  Type
                </th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-zinc-600 uppercase tracking-wide">
                  Status
                </th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-zinc-600 uppercase tracking-wide">
                  Records
                </th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-zinc-600 uppercase tracking-wide">
                  Time
                </th>
              </tr>
            </thead>
            <tbody>
              {syncLogs.map((log) => (
                <tr key={log.id} className="border-b border-zinc-100 hover:bg-zinc-50">
                  <td className="px-6 py-3">
                    <span className="text-sm font-medium text-zinc-900 capitalize">
                      {log.entity_type}
                    </span>
                  </td>
                  <td className="px-6 py-3">
                    <span className="text-sm text-zinc-600 capitalize">
                      {log.sync_type.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td className="px-6 py-3">
                    <span
                      className={`inline-flex items-center gap-1.5 text-xs font-medium ${
                        log.status === "completed"
                          ? "text-green-700"
                          : log.status === "failed"
                            ? "text-red-700"
                            : log.status === "running"
                              ? "text-blue-700"
                              : "text-zinc-600"
                      }`}
                    >
                      {log.status === "completed" ? (
                        <CheckCircle className="w-3.5 h-3.5" />
                      ) : log.status === "failed" ? (
                        <XCircle className="w-3.5 h-3.5" />
                      ) : log.status === "running" ? (
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      ) : (
                        <AlertTriangle className="w-3.5 h-3.5" />
                      )}
                      {log.status}
                    </span>
                    {log.error_message && (
                      <p className="text-xs text-red-500 mt-0.5 truncate max-w-xs" title={log.error_message}>
                        {log.error_message}
                      </p>
                    )}
                  </td>
                  <td className="px-6 py-3">
                    <span className="text-sm text-zinc-600">
                      {log.records_processed > 0
                        ? `${log.records_created} new, ${log.records_updated} updated${log.records_failed > 0 ? `, ${log.records_failed} failed` : ""}`
                        : "-"}
                    </span>
                  </td>
                  <td className="px-6 py-3">
                    <span className="text-sm text-zinc-500" suppressHydrationWarning>
                      {log.completed_at
                        ? new Date(log.completed_at).toLocaleString("en-US", {
                            month: "short",
                            day: "numeric",
                            hour: "numeric",
                            minute: "2-digit",
                          })
                        : log.started_at
                          ? "In progress..."
                          : "Pending"}
                    </span>
                    {log.duration_seconds !== null && (
                      <p className="text-xs text-zinc-400">{log.duration_seconds.toFixed(1)}s</p>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
