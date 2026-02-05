/**
 * Environment configuration for PawPoint Frontend
 *
 * This module provides type-safe access to environment variables.
 * All public environment variables must be prefixed with NEXT_PUBLIC_
 */

/**
 * Application environment
 */
export const env = {
    /**
     * Backend API URL for client-side calls (browser)
     * @default http://localhost:8000
     */
    apiUrl: process.env.NEXT_PUBLIC_API_URL || '',  // Use relative URLs - proxied through Next.js

    /**
     * Backend API URL for server-side calls (inside Docker container)
     * Uses Docker service name instead of localhost
     * @default http://backend:8000
     */
    serverApiUrl: process.env.API_URL || 'http://backend:8000',

    /**
     * Current environment
     */
    nodeEnv: process.env.NODE_ENV || 'development',

    /**
     * Is development mode
     */
    isDevelopment: process.env.NODE_ENV === 'development',

    /**
     * Is production mode
     */
    isProduction: process.env.NODE_ENV === 'production',

    /**
     * App version
     */
    appVersion: process.env.NEXT_PUBLIC_APP_VERSION || '0.1.0',

    /**
     * Feature flags
     */
    features: {
        analytics: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === 'true',
        voice: process.env.NEXT_PUBLIC_ENABLE_VOICE !== 'false', // Enabled by default
    },

    /**
     * LiveKit configuration for voice widget
     * Set NEXT_PUBLIC_LIVEKIT_WS_URL in production (e.g., wss://your-project.livekit.cloud)
     */
    livekit: {
        wsUrl: process.env.NEXT_PUBLIC_LIVEKIT_WS_URL || '',
    },

    /**
     * Third-party service IDs (only if public/client-side)
     */
    services: {
        gaMeasurementId: process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID,
        sentryDsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
    },
} as const;

/**
 * Get the appropriate API URL based on execution context
 * - Server-side: Uses internal Docker network (backend:8000)
 * - Client-side: Uses localhost or public URL (localhost:8000)
 *
 * @returns The correct API URL for the current context
 */
export function getApiUrl(): string {
    // Check if we're running on the server (Node.js) or client (browser)
    if (typeof window === 'undefined') {
        // Server-side: use internal Docker network URL
        return env.serverApiUrl;
    }
    // Client-side: use public API URL
    return env.apiUrl;
}

/**
 * Validate required environment variables at build/startup
 */
export function validateEnv(): void {
    const required = ['NEXT_PUBLIC_API_URL'] as const;
    const missing = required.filter((key) => !process.env[key]);

    if (missing.length > 0 && process.env.NODE_ENV === 'production') {
        console.warn(
            `⚠️ Missing recommended environment variables: ${missing.join(', ')}`
        );
    }
}
