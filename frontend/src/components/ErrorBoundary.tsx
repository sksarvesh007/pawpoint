"use client";

import { Component, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log to error tracking service in production
    if (process.env.NODE_ENV === "production") {
      // Don't log sensitive error details in production
      console.error("Dashboard error occurred");

      // Send to error tracking service (Sentry, etc.)
      if (
        typeof window !== "undefined" &&
        "Sentry" in window &&
        typeof (window as { Sentry?: { captureException: (error: Error, options?: Record<string, unknown>) => void } }).Sentry?.captureException === "function"
      ) {
        (window as { Sentry: { captureException: (error: Error, options?: Record<string, unknown>) => void } }).Sentry.captureException(error, {
          contexts: { react: errorInfo },
        });
      }
    } else {
      // In development, log full details
      console.error("Error boundary caught:", error, errorInfo);
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <h2 className="text-xl font-bold text-zinc-900 mb-2">
                Something went wrong
              </h2>
              <p className="text-zinc-600 mb-4">
                We encountered an error loading the dashboard
              </p>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
              >
                Reload Page
              </button>
            </div>
          </div>
        )
      );
    }

    return this.props.children;
  }
}
