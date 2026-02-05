/**
 * Voice API Client
 *
 * Functions for interacting with the voice API endpoints.
 */

import { getApiUrl } from '../env';
import type { VoiceStatusResponse, VoiceTokenResponse } from '@/types/voice';

const API_BASE_URL = getApiUrl();

/**
 * Generate a voice token for connecting to the voice widget
 *
 * @param clinicSlug - The clinic's URL slug
 * @returns Voice token response with room info
 */
export async function generateVoiceToken(
    clinicSlug: string
): Promise<VoiceTokenResponse> {
    const response = await fetch(
        `${API_BASE_URL}/api/v1/${clinicSlug}/voice/token`,
        {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
        }
    );

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Failed to generate voice token');
    }

    return response.json();
}

/**
 * Check if voice is available for a clinic
 *
 * @param clinicSlug - The clinic's URL slug
 * @returns Voice status with availability info
 */
export async function getVoiceStatus(
    clinicSlug: string
): Promise<VoiceStatusResponse> {
    const response = await fetch(
        `${API_BASE_URL}/api/v1/${clinicSlug}/voice/status`,
        {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
        }
    );

    if (!response.ok) {
        return {
            available: false,
            reason: 'Failed to check voice status',
        };
    }

    return response.json();
}
