'use client';

/**
 * Voice Widget Component
 *
 * A floating voice chat bubble for the dashboard that allows users
 * to interact with the AI assistant via voice.
 */

import { useState } from 'react';
import { Mic, MicOff, Phone, PhoneOff, X, Loader2, Wifi, WifiOff } from 'lucide-react';
import { useVoiceChat } from '@/hooks/useVoiceChat';
import type { VoiceWidgetProps } from '@/types/voice';

export function VoiceWidget({ clinicSlug, className = '' }: VoiceWidgetProps) {
    const [isExpanded, setIsExpanded] = useState(false);
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

    // Don't render if voice is not available
    if (!isAvailable) {
        return null;
    }

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
                return 'Connecting...';
            case 'connected':
                return 'Connected';
            case 'reconnecting':
                return 'Reconnecting...';
            case 'error':
                return 'Error';
            default:
                return 'Click to start voice chat';
        }
    };

    return (
        <div className={`fixed bottom-6 right-6 z-50 ${className}`}>
            {/* Expanded panel */}
            {isExpanded && (
                <div className="mb-4 w-80 rounded-lg bg-white shadow-xl border border-gray-200 overflow-hidden">
                    {/* Header */}
                    <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white">
                        <div className="flex items-center gap-2">
                            <Phone className="h-5 w-5" />
                            <span className="font-medium">Voice Assistant</span>
                        </div>
                        <button
                            onClick={() => setIsExpanded(false)}
                            className="p-1 hover:bg-white/20 rounded transition-colors"
                            aria-label="Close voice widget"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    </div>

                    {/* Content */}
                    <div className="p-4">
                        {/* Status */}
                        <div className="flex items-center justify-between mb-4">
                            <span className="text-sm text-gray-600">
                                {getStatusText()}
                            </span>
                            {isInCall && (
                                <div className="flex items-center gap-1">
                                    {connectionQuality === 'poor' ? (
                                        <WifiOff className={`h-4 w-4 ${getQualityColor()}`} />
                                    ) : (
                                        <Wifi className={`h-4 w-4 ${getQualityColor()}`} />
                                    )}
                                    <span className={`text-xs ${getQualityColor()}`}>
                                        {connectionQuality}
                                    </span>
                                </div>
                            )}
                        </div>

                        {/* Error message */}
                        {error && (
                            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                                <p className="text-sm text-red-600">{error}</p>
                            </div>
                        )}

                        {/* Visual indicator */}
                        <div className="flex justify-center mb-4">
                            <div
                                className={`w-24 h-24 rounded-full flex items-center justify-center transition-all duration-300 ${
                                    isInCall
                                        ? 'bg-gradient-to-r from-green-400 to-emerald-500'
                                        : 'bg-gray-100'
                                }`}
                            >
                                {connectionState === 'connecting' ||
                                connectionState === 'reconnecting' ? (
                                    <Loader2 className="h-10 w-10 text-indigo-500 animate-spin" />
                                ) : isInCall ? (
                                    <div className="relative">
                                        {/* Pulsing animation for active call */}
                                        <div className="absolute inset-0 rounded-full bg-white/30 animate-ping" />
                                        <Mic className="h-10 w-10 text-white relative z-10" />
                                    </div>
                                ) : (
                                    <Mic className="h-10 w-10 text-gray-400" />
                                )}
                            </div>
                        </div>

                        {/* Controls */}
                        <div className="flex justify-center gap-4">
                            {/* Mute button (only visible during call) */}
                            {isInCall && (
                                <button
                                    onClick={toggleMute}
                                    className={`p-4 rounded-full transition-colors ${
                                        isMuted
                                            ? 'bg-red-100 text-red-600 hover:bg-red-200'
                                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                    }`}
                                    aria-label={isMuted ? 'Unmute' : 'Mute'}
                                >
                                    {isMuted ? (
                                        <MicOff className="h-6 w-6" />
                                    ) : (
                                        <Mic className="h-6 w-6" />
                                    )}
                                </button>
                            )}

                            {/* Call button */}
                            <button
                                onClick={handleCallToggle}
                                disabled={
                                    connectionState === 'connecting' ||
                                    connectionState === 'reconnecting'
                                }
                                className={`p-4 rounded-full transition-colors ${
                                    isInCall
                                        ? 'bg-red-500 text-white hover:bg-red-600'
                                        : 'bg-green-500 text-white hover:bg-green-600'
                                } disabled:opacity-50 disabled:cursor-not-allowed`}
                                aria-label={isInCall ? 'End call' : 'Start call'}
                            >
                                {connectionState === 'connecting' ||
                                connectionState === 'reconnecting' ? (
                                    <Loader2 className="h-6 w-6 animate-spin" />
                                ) : isInCall ? (
                                    <PhoneOff className="h-6 w-6" />
                                ) : (
                                    <Phone className="h-6 w-6" />
                                )}
                            </button>
                        </div>

                        {/* Help text */}
                        <p className="mt-4 text-xs text-center text-gray-500">
                            {isInCall
                                ? 'Speak naturally to interact with our AI assistant'
                                : 'Click the green button to start a voice conversation'}
                        </p>
                    </div>
                </div>
            )}

            {/* Floating button */}
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className={`p-4 rounded-full shadow-lg transition-all duration-300 ${
                    isInCall
                        ? 'bg-gradient-to-r from-green-400 to-emerald-500 animate-pulse'
                        : 'bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700'
                }`}
                aria-label={isExpanded ? 'Close voice widget' : 'Open voice widget'}
            >
                {isInCall ? (
                    <Mic className="h-6 w-6 text-white" />
                ) : (
                    <Phone className="h-6 w-6 text-white" />
                )}
            </button>
        </div>
    );
}
