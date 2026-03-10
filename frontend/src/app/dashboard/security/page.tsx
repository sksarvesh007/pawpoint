/**
 * Security Settings page - Change password and manage account security.
 */

"use client";

import { useState, useEffect } from "react";
import {
  Shield,
  Lock,
  Loader2,
  X,
  Check,
  Eye,
  EyeOff,
} from "lucide-react";
import { env } from "@/lib/env";

export default function SecurityPage() {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(""), 4000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  const passwordChecks = [
    { label: "At least 8 characters", met: newPassword.length >= 8 },
    { label: "Uppercase letter", met: /[A-Z]/.test(newPassword) },
    { label: "Lowercase letter", met: /[a-z]/.test(newPassword) },
    { label: "Number", met: /\d/.test(newPassword) },
    {
      label: "Special character",
      met: /[!@#$%^&*(),.?":{}|<>\-_=+\[\]\\;'`~]/.test(newPassword),
    },
    {
      label: "Passwords match",
      met: newPassword.length > 0 && newPassword === confirmPassword,
    },
  ];

  const allChecksMet = passwordChecks.every((c) => c.met);

  const handleChangePassword = async () => {
    if (!allChecksMet) {
      setError("Please meet all password requirements");
      return;
    }

    setError("");
    setSaving(true);
    try {
      const response = await fetch(
        `${env.apiUrl}/api/v1/auth/change-password`,
        {
          method: "PUT",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword,
          }),
        }
      );

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(
          data?.detail || `Failed to change password: ${response.statusText}`
        );
      }

      setSuccess("Password changed successfully");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to change password"
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-2xl">
      <div className="mb-8">
        <h1 className="text-3xl font-nunito font-bold text-zinc-900 flex items-center gap-3">
          <Shield className="w-8 h-8 text-teal-600" />
          Security
        </h1>
        <p className="text-zinc-600 mt-1">
          Manage your password and account security
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
      {success && (
        <div className="mb-6 rounded-lg bg-green-50 p-4 text-sm text-green-600 flex items-center justify-between">
          <span>{success}</span>
          <button onClick={() => setSuccess("")}>
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Change Password */}
      <div className="bg-white rounded-xl border border-zinc-200 p-6 shadow-sm mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Lock className="w-5 h-5 text-zinc-700" />
          <h2 className="text-lg font-bold text-zinc-900">Change Password</h2>
        </div>

        <div className="space-y-4">
          {/* Current Password */}
          <div>
            <label className="block text-sm font-medium text-zinc-600 mb-1">
              Current Password
            </label>
            <div className="relative">
              <input
                type={showCurrent ? "text" : "password"}
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="w-full px-3 py-2.5 border border-zinc-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent pr-10"
                placeholder="Enter current password"
              />
              <button
                type="button"
                onClick={() => setShowCurrent(!showCurrent)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600"
              >
                {showCurrent ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          {/* New Password */}
          <div>
            <label className="block text-sm font-medium text-zinc-600 mb-1">
              New Password
            </label>
            <div className="relative">
              <input
                type={showNew ? "text" : "password"}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full px-3 py-2.5 border border-zinc-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent pr-10"
                placeholder="Enter new password"
              />
              <button
                type="button"
                onClick={() => setShowNew(!showNew)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600"
              >
                {showNew ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-sm font-medium text-zinc-600 mb-1">
              Confirm New Password
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-3 py-2.5 border border-zinc-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              placeholder="Confirm new password"
            />
          </div>

          {/* Password Strength Checklist */}
          {newPassword.length > 0 && (
            <div className="bg-zinc-50 rounded-lg p-4 space-y-2">
              {passwordChecks.map((check) => (
                <div
                  key={check.label}
                  className="flex items-center gap-2 text-sm"
                >
                  {check.met ? (
                    <Check className="w-4 h-4 text-green-600" />
                  ) : (
                    <X className="w-4 h-4 text-zinc-300" />
                  )}
                  <span
                    className={
                      check.met ? "text-green-700" : "text-zinc-500"
                    }
                  >
                    {check.label}
                  </span>
                </div>
              ))}
            </div>
          )}

          <button
            onClick={handleChangePassword}
            disabled={saving || !allChecksMet || !currentPassword}
            className="flex items-center gap-2 px-5 py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 disabled:opacity-50"
          >
            {saving ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Lock className="w-4 h-4" />
            )}
            Change Password
          </button>
        </div>
      </div>

      {/* Account Info */}
      <div className="bg-white rounded-xl border border-zinc-200 p-6 shadow-sm">
        <h2 className="text-lg font-bold text-zinc-900 mb-4">
          Account Security
        </h2>
        <div className="space-y-3 text-sm">
          <div className="flex items-center justify-between py-2 border-b border-zinc-100">
            <span className="text-zinc-600">Authentication</span>
            <span className="text-zinc-900 font-medium">
              Email & Password
            </span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-zinc-100">
            <span className="text-zinc-600">Session</span>
            <span className="text-zinc-900 font-medium">
              HTTP-only cookie (secure)
            </span>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="text-zinc-600">Two-Factor Authentication</span>
            <span className="text-xs text-zinc-500 bg-zinc-100 px-2 py-1 rounded">
              Coming Soon
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
