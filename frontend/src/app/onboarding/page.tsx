"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function OnboardingPage() {
  const router = useRouter();

  useEffect(() => {
    // Immediately redirect to chatbot onboarding
    // This page exists just to have a clean /onboarding route
    router.push("/onboarding/chatbot");
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
        <p className="mt-4 text-sm text-zinc-600 dark:text-zinc-400">
          Loading onboarding...
        </p>
      </div>
    </div>
  );
}
