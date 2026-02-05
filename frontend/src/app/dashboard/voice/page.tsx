'use client';

/**
 * Voice Bot Page
 *
 * Full-screen voice assistant interface for interacting with
 * the AI voice bot via LiveKit.
 */

import { useEffect, useState } from 'react';
import {
    Mic,
    MicOff,
    Phone,
    PhoneOff,
    Loader2,
    Wifi,
    WifiOff,
    Volume2,
    Settings,
    Info,
} from 'lucide-react';
import { useVoiceChat } from '@/hooks/useVoiceChat';
import { getClinicInfo } from '@/lib/api/clinic';

export default function VoiceBotPage() {
    const [clinicSlug, setClinicSlug] = useState<string>('');
    const [clinicName, setClinicName] = useState<string>('');
    const [isLoading, setIsLoading] = useState(true);

    // Fetch clinic info on mount
    useEffect(() => {
        getClinicInfo()
            .then((info) => {
                setClinicSlug(info.slug);
                setClinicName(info.name);
                setIsLoading(false);
            })
            .catch(() => {
                setIsLoading(false);
            });
    }, []);

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
                <Loader2 className="h-8 w-8 animate-spin text-[#3EB5B0]" />
            </div>
        );
    }

    if (!clinicSlug) {
        return (
            <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
                <div className="text-center">
                    <Info className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h2 className="text-xl font-semibold text-gray-700">Unable to load clinic</h2>
                    <p className="text-gray-500 mt-2">Please try refreshing the page.</p>
                </div>
            </div>
        );
    }

    return <VoiceBotInterface clinicSlug={clinicSlug} clinicName={clinicName} />;
}

interface VoiceBotInterfaceProps {
    clinicSlug: string;
    clinicName: string;
}

function VoiceBotInterface({ clinicSlug, clinicName }: VoiceBotInterfaceProps) {
    const {
        connectionState,
        isAvailable,
        isInCall,
        isMuted,
        connect,
        disconnect,
        toggleMute,
        error,
        connectionQuality,
    } = useVoiceChat(clinicSlug);

    const [callDuration, setCallDuration] = useState(0);

    // Call duration timer - resets when call starts
    useEffect(() => {
        if (!isInCall) {
            return;
        }
        // eslint-disable-next-line react-hooks/set-state-in-effect -- Intentional reset when call starts
        setCallDuration(0);
        const interval = setInterval(() => {
            setCallDuration((prev) => prev + 1);
        }, 1000);
        return () => clearInterval(interval);
    }, [isInCall]);

    const formatDuration = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    const handleCallToggle = async () => {
        if (isInCall) {
            await disconnect();
        } else {
            await connect();
        }
    };

    const getQualityColor = () => {
        switch (connectionQuality) {
            case 'excellent':
                return 'text-green-500';
            case 'good':
                return 'text-yellow-500';
            case 'poor':
                return 'text-red-500';
            default:
                return 'text-gray-400';
        }
    };

    const getStatusText = () => {
        switch (connectionState) {
            case 'connecting':
                return 'Connecting to voice assistant...';
            case 'connected':
                return 'Connected - Speak naturally';
            case 'reconnecting':
                return 'Reconnecting...';
            case 'error':
                return 'Connection error';
            default:
                return 'Ready to connect';
        }
    };

    if (!isAvailable) {
        return (
            <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
                <div className="text-center max-w-md mx-auto p-8">
                    <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                        <MicOff className="h-10 w-10 text-gray-400" />
                    </div>
                    <h2 className="text-2xl font-semibold text-gray-700 mb-3">
                        Voice Bot Not Available
                    </h2>
                    <p className="text-gray-500">
                        The voice assistant is not currently enabled for this clinic.
                        Please contact support to enable this feature.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-[calc(100vh-4rem)] flex flex-col">
            {/* Header */}
            <div className="bg-white/70 backdrop-blur-sm border-b border-gray-200/50 px-6 py-4">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-[#1D3533]">Voice Assistant</h1>
                        <p className="text-sm text-gray-500 mt-1">{clinicName}</p>
                    </div>
                    {isInCall && (
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2 px-3 py-1.5 bg-green-100 rounded-full">
                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                                <span className="text-sm font-medium text-green-700">
                                    {formatDuration(callDuration)}
                                </span>
                            </div>
                            <div className="flex items-center gap-1">
                                {connectionQuality === 'poor' ? (
                                    <WifiOff className={`h-5 w-5 ${getQualityColor()}`} />
                                ) : (
                                    <Wifi className={`h-5 w-5 ${getQualityColor()}`} />
                                )}
                                <span className={`text-sm capitalize ${getQualityColor()}`}>
                                    {connectionQuality}
                                </span>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Main content */}
            <div className="flex-1 flex flex-col items-center justify-center p-8">
                {/* Error message */}
                {error && (
                    <div className="mb-8 max-w-md w-full p-4 bg-red-50 border border-red-200 rounded-xl">
                        <p className="text-sm text-red-600 text-center">{error}</p>
                    </div>
                )}

                {/* Visual indicator */}
                <div className="relative mb-8">
                    {/* Outer rings for active call */}
                    {isInCall && (
                        <>
                            <div className="absolute inset-0 -m-8 rounded-full bg-[#3EB5B0]/10 animate-ping" />
                            <div className="absolute inset-0 -m-4 rounded-full bg-[#3EB5B0]/20 animate-pulse" />
                        </>
                    )}

                    <div
                        className={`w-40 h-40 rounded-full flex items-center justify-center transition-all duration-500 shadow-lg ${
                            isInCall
                                ? 'bg-gradient-to-br from-[#3EB5B0] to-[#2A8A86]'
                                : 'bg-gradient-to-br from-gray-100 to-gray-200'
                        }`}
                    >
                        {connectionState === 'connecting' || connectionState === 'reconnecting' ? (
                            <Loader2 className="h-16 w-16 text-[#3EB5B0] animate-spin" />
                        ) : isInCall ? (
                            <div className="relative">
                                <Volume2 className="h-16 w-16 text-white animate-pulse" />
                            </div>
                        ) : (
                            <Mic className="h-16 w-16 text-gray-400" />
                        )}
                    </div>
                </div>

                {/* Status text */}
                <p
                    className={`text-lg font-medium mb-2 ${
                        isInCall ? 'text-[#1D3533]' : 'text-gray-600'
                    }`}
                >
                    {getStatusText()}
                </p>
                <p className="text-sm text-gray-500 mb-12 max-w-sm text-center">
                    {isInCall
                        ? 'Ask about appointments, clinic hours, or any questions about your pet'
                        : 'Start a voice conversation with our AI assistant to book appointments, ask questions, or get help'}
                </p>

                {/* Controls */}
                <div className="flex items-center gap-6">
                    {/* Mute button (only visible during call) */}
                    {isInCall && (
                        <button
                            onClick={toggleMute}
                            className={`p-5 rounded-full transition-all shadow-lg ${
                                isMuted
                                    ? 'bg-red-100 text-red-600 hover:bg-red-200'
                                    : 'bg-white text-gray-600 hover:bg-gray-50'
                            }`}
                            aria-label={isMuted ? 'Unmute' : 'Mute'}
                        >
                            {isMuted ? (
                                <MicOff className="h-7 w-7" />
                            ) : (
                                <Mic className="h-7 w-7" />
                            )}
                        </button>
                    )}

                    {/* Main call button */}
                    <button
                        onClick={handleCallToggle}
                        disabled={connectionState === 'connecting' || connectionState === 'reconnecting'}
                        className={`p-6 rounded-full transition-all shadow-xl ${
                            isInCall
                                ? 'bg-red-500 text-white hover:bg-red-600 hover:scale-105'
                                : 'bg-gradient-to-br from-[#3EB5B0] to-[#2A8A86] text-white hover:from-[#35A09C] hover:to-[#237571] hover:scale-105'
                        } disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100`}
                        aria-label={isInCall ? 'End call' : 'Start call'}
                    >
                        {connectionState === 'connecting' || connectionState === 'reconnecting' ? (
                            <Loader2 className="h-8 w-8 animate-spin" />
                        ) : isInCall ? (
                            <PhoneOff className="h-8 w-8" />
                        ) : (
                            <Phone className="h-8 w-8" />
                        )}
                    </button>

                    {/* Settings button (placeholder) */}
                    {isInCall && (
                        <button
                            className="p-5 rounded-full bg-white text-gray-600 hover:bg-gray-50 transition-all shadow-lg"
                            aria-label="Settings"
                        >
                            <Settings className="h-7 w-7" />
                        </button>
                    )}
                </div>

                {/* Button label */}
                <p className="mt-6 text-sm text-gray-500">
                    {isInCall ? 'Click to end call' : 'Click to start voice chat'}
                </p>
            </div>

            {/* Footer tips */}
            {!isInCall && (
                <div className="bg-white/50 backdrop-blur-sm border-t border-gray-200/50 px-6 py-4">
                    <div className="max-w-2xl mx-auto">
                        <h3 className="text-sm font-semibold text-gray-700 mb-3">
                            What you can ask:
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                            <div className="flex items-start gap-2 text-sm text-gray-600">
                                <span className="text-[#3EB5B0]">&bull;</span>
                                &quot;I&apos;d like to book an appointment&quot;
                            </div>
                            <div className="flex items-start gap-2 text-sm text-gray-600">
                                <span className="text-[#3EB5B0]">&bull;</span>
                                &quot;What are your clinic hours?&quot;
                            </div>
                            <div className="flex items-start gap-2 text-sm text-gray-600">
                                <span className="text-[#3EB5B0]">&bull;</span>
                                &quot;My pet needs urgent care&quot;
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
