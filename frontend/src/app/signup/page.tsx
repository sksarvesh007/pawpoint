"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { env } from "@/lib/env";
import { Logo, NAVBAR_HEIGHT } from "@/components/Logo";
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
        credentials: "include",
        body: JSON.stringify({
          clinic_name: formData.clinicName,
          email: formData.email,
          password: formData.password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
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

      router.push("/onboarding/chatbot");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-white relative overflow-hidden">
      {/* Background Waves */}
      <div className="absolute inset-0 pointer-events-none">
        <svg
          className="absolute top-0 left-0 w-full h-full"
          viewBox="0 0 1440 900"
          preserveAspectRatio="xMidYMid slice"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <linearGradient id="signupWave1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#2A9D8F" stopOpacity="0.15" />
              <stop offset="50%" stopColor="#3DA99F" stopOpacity="0.2" />
              <stop offset="100%" stopColor="#7ECDC8" stopOpacity="0.15" />
            </linearGradient>
            <linearGradient id="signupWave2" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#7ECDC8" stopOpacity="0.1" />
              <stop offset="50%" stopColor="#2A9D8F" stopOpacity="0.15" />
              <stop offset="100%" stopColor="#3DA99F" stopOpacity="0.1" />
            </linearGradient>
            <linearGradient id="signupWave3" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3DA99F" stopOpacity="0.08" />
              <stop offset="100%" stopColor="#2A9D8F" stopOpacity="0.12" />
            </linearGradient>
          </defs>

          <path
            d="M-100,500 C200,650 400,300 720,400 C1040,500 1200,250 1540,350 L1540,900 L-100,900 Z"
            fill="url(#signupWave1)"
          />
          <path
            d="M-100,550 C150,400 350,600 650,450 C950,300 1150,550 1540,400 L1540,900 L-100,900 Z"
            fill="url(#signupWave2)"
          />
          <path
            d="M-100,600 C200,450 500,650 800,500 C1100,350 1300,600 1540,450 L1540,900 L-100,900 Z"
            fill="url(#signupWave3)"
          />
        </svg>
      </div>

      {/* Header */}
      <header
        className="flex items-center justify-between px-6 md:px-12 bg-white/80 backdrop-blur-sm border-b border-zinc-100 shadow-sm relative z-20"
        style={{ height: `${NAVBAR_HEIGHT}px` }}
      >
        <Link href="/" className="flex items-center gap-2">
          <Logo />
        </Link>
      </header>

      {/* Signup Form */}
      <main className="flex flex-1 items-center justify-center px-6 py-12 relative z-10">
        <div className="w-full max-w-md">
          <div className="rounded-2xl border border-zinc-200/60 bg-white/70 backdrop-blur-md p-8 shadow-xl">
            <h1 className="text-2xl font-nunito font-bold text-[#1D3533]">
              Register your clinic
            </h1>
            <p className="mt-2 text-sm text-zinc-600">
              Create an account to get started with PawPoint
            </p>

            <form onSubmit={handleSubmit} className="mt-8 space-y-5">
              {error && (
                <div
                  role="alert"
                  aria-live="polite"
                  className="rounded-lg bg-red-50 p-3 text-sm text-red-600"
                >
                  {error}
                </div>
              )}

              <div>
                <label
                  htmlFor="clinicName"
                  className="block text-sm font-medium text-zinc-700"
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
                  className="mt-2 block w-full rounded-lg border border-zinc-300 bg-white/80 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                  placeholder="Happy Paws Veterinary"
                />
              </div>

              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-zinc-700"
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
                  className="mt-2 block w-full rounded-lg border border-zinc-300 bg-white/80 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                  placeholder="clinic@example.com"
                />
              </div>

              <div>
                <label
                  htmlFor="password"
                  className="block text-sm font-medium text-zinc-700"
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
                  className="mt-2 block w-full rounded-lg border border-zinc-300 bg-white/80 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                  placeholder="••••••••"
                />
                <p className="mt-1 text-xs text-zinc-500">
                  Must be 8+ characters with uppercase, lowercase, number, and
                  special character
                </p>
              </div>

              <div>
                <label
                  htmlFor="confirmPassword"
                  className="block text-sm font-medium text-zinc-700"
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
                  className="mt-2 block w-full rounded-lg border border-zinc-300 bg-white/80 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                  placeholder="••••••••"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg bg-[#3DA99F] py-3 text-sm font-bold text-white hover:bg-[#2A9D8F] focus:outline-none focus:ring-2 focus:ring-[#3DA99F] focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors shadow-lg shadow-[#3DA99F]/25"
              >
                {loading ? "Creating account..." : "Create account"}
              </button>
            </form>

            <p className="mt-6 text-center text-sm text-zinc-600">
              Already have an account?{" "}
              <Link
                href="/login"
                className="font-medium text-[#3DA99F] hover:text-[#2A9D8F]"
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
