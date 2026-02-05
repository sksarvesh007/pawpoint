/**
 * Voice Chat Types
 *
 * Types for the browser voice widget integration with LiveKit.
 */

/**
 * Voice token response from the API
 */
export interface VoiceTokenResponse {
    token: string;
    room_name: string;
    ws_url: string;
}

/**
 * Voice status response from the API
 */
export interface VoiceStatusResponse {
    available: boolean;
    reason?: string;
    greeting_message?: string;
    chatbot_persona?: string;
}

/**
 * Voice connection states
 */
export type VoiceConnectionState =
    | 'disconnected'
    | 'connecting'
    | 'connected'
    | 'reconnecting'
    | 'error';

/**
 * Voice chat hook return type
 */
export interface UseVoiceChatReturn {
    /** Current connection state */
    connectionState: VoiceConnectionState;
    /** Whether voice is available for this clinic */
    isAvailable: boolean;
    /** Whether currently in a call */
    isInCall: boolean;
    /** Whether microphone is muted */
    isMuted: boolean;
    /** Connect to voice chat */
    connect: () => Promise<void>;
    /** Disconnect from voice chat */
    disconnect: () => Promise<void>;
    /** Toggle microphone mute */
    toggleMute: () => void;
    /** Error message if any */
    error: string | null;
    /** Connection quality indicator */
    connectionQuality: 'excellent' | 'good' | 'poor' | 'unknown';
}

/**
 * Voice widget props
 */
export interface VoiceWidgetProps {
    /** Clinic slug for API calls */
    clinicSlug: string;
    /** Custom class name */
    className?: string;
}
