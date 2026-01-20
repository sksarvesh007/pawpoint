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
     * Backend API URL
     * @default http://localhost:8000
     */
    apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',

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
        voice: process.env.NEXT_PUBLIC_ENABLE_VOICE === 'true',
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
