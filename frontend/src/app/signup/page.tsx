"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { env } from "@/lib/env";
import type { TokenResponse, ErrorResponse } from "@/types/auth";

export default function SignupPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    clinicName: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    // Client-side password validation (backend also validates)
    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    if (!/[A-Z]/.test(formData.password)) {
      setError("Password must contain at least one uppercase letter");
      return;
    }

    if (!/[a-z]/.test(formData.password)) {
      setError("Password must contain at least one lowercase letter");
      return;
    }

    if (!/\d/.test(formData.password)) {
      setError("Password must contain at least one digit");
      return;
    }

    if (!/[!@#$%^&*(),.?":{}|<>\-_=+\[\]\\;'`~]/.test(formData.password)) {
      setError("Password must contain at least one special character");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${env.apiUrl}/api/v1/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", // Include cookies for httpOnly auth
        body: JSON.stringify({
          clinic_name: formData.clinicName,
          email: formData.email,
          password: formData.password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Specific error handling based on status
        let errorMessage = "Registration failed. Please try again.";

        if (response.status === 400) {
          errorMessage =
            (data as ErrorResponse).detail ||
            "Please check your information and try again.";
        } else if (response.status === 429) {
          errorMessage =
            "Too many registration attempts. Please try again later.";
        } else if (response.status >= 500) {
          errorMessage =
            "We're experiencing technical difficulties. Please try again in a few minutes.";
        }

        throw new Error(errorMessage);
      }

      // Token is now stored in httpOnly cookie by the backend
      // No need to store in localStorage - redirect directly
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-blue-50 to-white dark:from-zinc-900 dark:to-black">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 md:px-12">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-white font-bold text-xl">
            P
          </div>
          <span className="text-xl font-semibold text-zinc-900 dark:text-white">
            PawPoint
          </span>
        </Link>
      </header>

      {/* Signup Form */}
      <main className="flex flex-1 items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <div className="rounded-xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
            <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">
              Register your clinic
            </h1>
            <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
              Create an account to get started with PawPoint
            </p>

            <form onSubmit={handleSubmit} className="mt-8 space-y-6">
              {error && (
                <div
                  role="alert"
                  aria-live="polite"
                  className="rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400"
                >
                  {error}
                </div>
              )}

              <div>
                <label
                  htmlFor="clinicName"
                  className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
                >
                  Clinic Name
                </label>
                <input
                  type="text"
                  id="clinicName"
                  name="clinicName"
                  value={formData.clinicName}
                  onChange={handleChange}
                  required
                  className="mt-2 block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-800 dark:text-white dark:placeholder-zinc-500"
                  placeholder="Happy Paws Veterinary"
                />
              </div>

              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
                >
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="mt-2 block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-800 dark:text-white dark:placeholder-zinc-500"
                  placeholder="clinic@example.com"
                />
              </div>

              <div>
                <label
                  htmlFor="password"
                  className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
                >
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  className="mt-2 block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-800 dark:text-white dark:placeholder-zinc-500"
                  placeholder="••••••••"
                />
                <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
                  Must be 8+ characters with uppercase, lowercase, number, and
                  special character
                </p>
              </div>

              <div>
                <label
                  htmlFor="confirmPassword"
                  className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
                >
                  Confirm Password
                </label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  className="mt-2 block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-800 dark:text-white dark:placeholder-zinc-500"
                  placeholder="••••••••"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg bg-blue-600 py-3 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
              >
                {loading ? "Creating account..." : "Create account"}
              </button>
            </form>

            <p className="mt-6 text-center text-sm text-zinc-600 dark:text-zinc-400">
              Already have an account?{" "}
              <Link
                href="/login"
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                Log in
              </Link>
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
