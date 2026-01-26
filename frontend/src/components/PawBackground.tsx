import Image from "next/image";

interface PawBackgroundProps {
    /** Number of paw prints to show */
    pawCount?: number;
    /** Number of circles to show */
    circleCount?: number;
    /** Opacity of paw prints (0-1) */
    pawOpacity?: number;
    /** Opacity of circles (0-1) */
    circleOpacity?: number;
    /** Size range for paws [min, max] in pixels */
    pawSizeRange?: [number, number];
    /** Size range for circles [min, max] in pixels */
    circleSizeRange?: [number, number];
    /** Additional CSS classes */
    className?: string;
}

export const PawBackground = ({
    pawCount = 12,
    circleCount = 6,
    pawOpacity = 0.15,
    circleOpacity = 0.08,
    pawSizeRange = [30, 70],
    circleSizeRange = [100, 400],
    className = "",
}: PawBackgroundProps) => {
    // Helper function to check if two paws are too close
    const isTooClose = (x1: number, y1: number, x2: number, y2: number, minDistance: number) => {
        const distance = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
        return distance < minDistance;
    };

    // Generate random positions and properties for paws with spacing
    const paws = (() => {
        const generatedPaws: Array<{ id: number; size: number; top: string; left: string; rotation: number; x: number; y: number }> = [];
        const minDistance = 15; // Minimum distance between paws (in percentage)
        let attempts = 0;
        const maxAttempts = 1000;

        while (generatedPaws.length < pawCount && attempts < maxAttempts) {
            attempts++;
            const size = Math.random() * (pawSizeRange[1] - pawSizeRange[0]) + pawSizeRange[0];
            const top = Math.random() * 100;
            const left = Math.random() * 100;
            const rotation = Math.random() * 360 - 180;

            // Check if this position is too close to any existing paw
            const tooClose = generatedPaws.some(paw =>
                isTooClose(left, top, paw.x, paw.y, minDistance)
            );

            if (!tooClose) {
                generatedPaws.push({
                    id: generatedPaws.length,
                    size,
                    top: `${top}%`,
                    left: `${left}%`,
                    rotation,
                    x: left,
                    y: top,
                });
            }
        }

        return generatedPaws;
    })();

    // Generate random positions and properties for circles
    const circles = Array.from({ length: circleCount }, (_, i) => {
        const size = Math.random() * (circleSizeRange[1] - circleSizeRange[0]) + circleSizeRange[0];
        const top = Math.random() * 100;
        const left = Math.random() * 100;
        const animationDelay = Math.random() * 3;
        const animationDuration = 4 + Math.random() * 4;

        return {
            id: i,
            size,
            top: `${top}%`,
            left: `${left}%`,
            animationDelay: `${animationDelay}s`,
            animationDuration: `${animationDuration}s`,
        };
    });

    return (
        <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
            {/* Translucent circles */}
            {circles.map((circle) => (
                <div
                    key={`circle-${circle.id}`}
                    className="absolute rounded-full bg-gradient-to-br from-[#C5E8E6] to-[#7ECDC8] animate-pulse"
                    style={{
                        width: `${circle.size}px`,
                        height: `${circle.size}px`,
                        top: circle.top,
                        left: circle.left,
                        opacity: circleOpacity,
                        transform: 'translate(-50%, -50%)',
                        animationDelay: circle.animationDelay,
                        animationDuration: circle.animationDuration,
                    }}
                />
            ))}

            {/* Paw prints */}
            {paws.map((paw) => (
                <div
                    key={`paw-${paw.id}`}
                    className="absolute"
                    style={{
                        top: paw.top,
                        left: paw.left,
                        opacity: pawOpacity,
                        transform: `translate(-50%, -50%) rotate(${paw.rotation}deg)`,
                    }}
                >
                    <Image
                        src="/paws.png"
                        alt="Paw print"
                        width={paw.size}
                        height={paw.size}
                    />
                </div>
            ))}
        </div>
    );
};
