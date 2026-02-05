'use client';

/**
 * Voice Chat Hook
 *
 * Manages LiveKit room connection for the browser voice widget.
 * Handles connection, reconnection, and microphone state.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import {
    ConnectionQuality,
    ConnectionState,
    DisconnectReason,
    Room,
    RoomEvent,
    Track,
    RemoteTrack,
    RemoteTrackPublication,
    RemoteParticipant,
} from 'livekit-client';
import { generateVoiceToken, getVoiceStatus } from '@/lib/api/voice';
import { env } from '@/lib/env';
import type {
    UseVoiceChatReturn,
    VoiceConnectionState,
} from '@/types/voice';

/**
 * Hook for managing voice chat connections
 *
 * @param clinicSlug - The clinic's URL slug
 * @returns Voice chat state and controls
 */
export function useVoiceChat(clinicSlug: string): UseVoiceChatReturn {
    // State
    const [connectionState, setConnectionState] =
        useState<VoiceConnectionState>('disconnected');
    const [isAvailable, setIsAvailable] = useState(false);
    const [isInCall, setIsInCall] = useState(false);
    const [isMuted, setIsMuted] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [connectionQuality, setConnectionQuality] = useState<
        'excellent' | 'good' | 'poor' | 'unknown'
    >('unknown');

    // Refs
    const roomRef = useRef<Room | null>(null);
    const audioElementRef = useRef<HTMLAudioElement | null>(null);
    const reconnectAttempts = useRef(0);
    const maxReconnectAttempts = 3;

    // Create audio element for playing remote audio
    useEffect(() => {
        const audio = new Audio();
        audio.autoplay = true;
        audioElementRef.current = audio;

        return () => {
            if (audioElementRef.current) {
                audioElementRef.current.srcObject = null;
            }
        };
    }, []);

    // Check if voice is available
    useEffect(() => {
        const checkAvailability = async () => {
            // Check feature flag first
            if (!env.features.voice) {
                setIsAvailable(false);
                return;
            }

            try {
                const status = await getVoiceStatus(clinicSlug);
                setIsAvailable(status.available);
            } catch {
                setIsAvailable(false);
            }
        };

        checkAvailability();
    }, [clinicSlug]);

    // Map LiveKit connection quality to our simplified version
    const mapConnectionQuality = useCallback(
        (quality: ConnectionQuality): 'excellent' | 'good' | 'poor' | 'unknown' => {
            switch (quality) {
                case ConnectionQuality.Excellent:
                    return 'excellent';
                case ConnectionQuality.Good:
                    return 'good';
                case ConnectionQuality.Poor:
                case ConnectionQuality.Lost:
                    return 'poor';
                default:
                    return 'unknown';
            }
        },
        []
    );

    // Set up room event listeners
    const setupRoomListeners = useCallback(
        (room: Room) => {
            room.on(RoomEvent.ConnectionStateChanged, (state: ConnectionState) => {
                switch (state) {
                    case ConnectionState.Connected:
                        setConnectionState('connected');
                        setIsInCall(true);
                        setError(null);
                        reconnectAttempts.current = 0;
                        break;
                    case ConnectionState.Connecting:
                        setConnectionState('connecting');
                        break;
                    case ConnectionState.Reconnecting:
                        setConnectionState('reconnecting');
                        break;
                    case ConnectionState.Disconnected:
                        setConnectionState('disconnected');
                        setIsInCall(false);
                        break;
                }
            });

            room.on(RoomEvent.Disconnected, (reason?: DisconnectReason) => {
                setIsInCall(false);

                // Auto-reconnect on network issues (not user-initiated)
                if (
                    reason !== DisconnectReason.CLIENT_INITIATED &&
                    reconnectAttempts.current < maxReconnectAttempts
                ) {
                    reconnectAttempts.current += 1;
                    console.log(
                        `Attempting reconnect (${reconnectAttempts.current}/${maxReconnectAttempts})`
                    );
                    // The room will auto-reconnect
                }
            });

            room.on(
                RoomEvent.ConnectionQualityChanged,
                (quality: ConnectionQuality) => {
                    setConnectionQuality(mapConnectionQuality(quality));
                }
            );

            room.on(RoomEvent.MediaDevicesError, (err: Error) => {
                console.error('Media device error:', err);
                if (err.name === 'NotAllowedError') {
                    setError(
                        'Microphone permission denied. Please allow microphone access to use voice chat.'
                    );
                } else {
                    setError('Microphone error: ' + err.message);
                }
            });

            // Handle incoming audio tracks from the agent
            room.on(
                RoomEvent.TrackSubscribed,
                (
                    track: RemoteTrack,
                    publication: RemoteTrackPublication,
                    participant: RemoteParticipant
                ) => {
                    console.log(`Track subscribed: ${track.kind} from ${participant.identity}`);
                    if (track.kind === Track.Kind.Audio) {
                        // Attach audio track to audio element for playback
                        const audioElement = audioElementRef.current;
                        if (audioElement) {
                            track.attach(audioElement);
                            console.log('Audio track attached to element');
                        }
                    }
                }
            );

            room.on(
                RoomEvent.TrackUnsubscribed,
                (
                    track: RemoteTrack,
                    publication: RemoteTrackPublication,
                    participant: RemoteParticipant
                ) => {
                    console.log(`Track unsubscribed: ${track.kind} from ${participant.identity}`);
                    if (track.kind === Track.Kind.Audio) {
                        track.detach();
                    }
                }
            );
        },
        [mapConnectionQuality]
    );

    // Connect to voice chat
    const connect = useCallback(async () => {
        if (!isAvailable) {
            setError('Voice chat is not available');
            return;
        }

        setConnectionState('connecting');
        setError(null);

        try {
            // Request microphone permission first
            await navigator.mediaDevices.getUserMedia({ audio: true });

            // Get token from backend
            const { token, ws_url } = await generateVoiceToken(clinicSlug);

            // Create room
            const room = new Room({
                adaptiveStream: true,
                dynacast: true,
            });

            roomRef.current = room;
            setupRoomListeners(room);

            // Connect to LiveKit
            const wsUrl = ws_url || env.livekit.wsUrl;
            await room.connect(wsUrl, token);

            // Enable microphone
            await room.localParticipant.setMicrophoneEnabled(true);
        } catch (err) {
            console.error('Voice connection error:', err);
            setConnectionState('error');

            if (err instanceof Error) {
                if (err.name === 'NotAllowedError') {
                    setError('Microphone permission denied');
                } else {
                    setError(err.message);
                }
            } else {
                setError('Failed to connect to voice chat');
            }
        }
    }, [clinicSlug, isAvailable, setupRoomListeners]);

    // Disconnect from voice chat
    const disconnect = useCallback(async () => {
        if (roomRef.current) {
            await roomRef.current.disconnect();
            roomRef.current = null;
        }
        // Clean up audio element
        if (audioElementRef.current) {
            audioElementRef.current.srcObject = null;
        }
        setConnectionState('disconnected');
        setIsInCall(false);
        setIsMuted(false);
        setConnectionQuality('unknown');
    }, []);

    // Toggle microphone mute
    const toggleMute = useCallback(() => {
        if (roomRef.current) {
            const newMuted = !isMuted;
            roomRef.current.localParticipant
                .setMicrophoneEnabled(!newMuted)
                .catch((err) => {
                    console.error('Failed to toggle mute:', err);
                });
            setIsMuted(newMuted);
        }
    }, [isMuted]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (roomRef.current) {
                roomRef.current.disconnect();
            }
        };
    }, []);

    return {
        connectionState,
        isAvailable,
        isInCall,
        isMuted,
        connect,
        disconnect,
        toggleMute,
        error,
        connectionQuality,
    };
}
