'use client';

/**
 * Voice Widget Container
 *
 * Client-side container that manages the VoiceWidget with clinic context.
 * This component handles getting the clinic slug from the current context.
 */

import { useState, useEffect } from 'react';
import { VoiceWidget } from './VoiceWidget';
import { env } from '@/lib/env';
import { getClinicInfo } from '@/lib/api/clinic';

interface VoiceWidgetContainerProps {
    clinicSlug?: string;
}

export function VoiceWidgetContainer({
    clinicSlug: propClinicSlug,
}: VoiceWidgetContainerProps) {
    const [clinicSlug, setClinicSlug] = useState<string | null>(propClinicSlug || null);

    useEffect(() => {
        if (propClinicSlug) {
            return;
        }

        // Fetch clinic info to get the slug
        getClinicInfo()
            .then((info) => {
                setClinicSlug(info.slug);
            })
            .catch(() => {
                // If we can't get clinic info, don't show the widget
                setClinicSlug(null);
            });
    }, [propClinicSlug]);

    // Only render if voice feature is enabled and we have a clinic slug
    if (!env.features.voice || !clinicSlug) {
        return null;
    }

    return <VoiceWidget clinicSlug={clinicSlug} />;
}
