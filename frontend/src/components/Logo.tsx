import Image from "next/image";

// Change LOGO_HEIGHT to adjust logo size across entire site
const LOGO_HEIGHT = 180; // in pixels (h-16 = 64px)

// Aspect ratio based on actual image dimensions (280:62 ≈ 4.5:1)
const ASPECT_RATIO = 4.5;

const LOGO_WIDTH = LOGO_HEIGHT * ASPECT_RATIO;

// Change NAVBAR_HEIGHT to adjust navbar height across entire site
export const NAVBAR_HEIGHT = 100; // in pixels - controls the fixed navbar height

interface LogoProps {
  align?: "left" | "center" | "right";
  paddingTop?: string;
  paddingLeft?: string;
  className?: string;
  height?: number;
}

export function Logo({
  align = "left",
  paddingTop = "20px",
  paddingLeft = "0px",
  className = "",
  height = LOGO_HEIGHT,
}: LogoProps = {}) {
  const objectPosition =
    align === "left" ? "left center" : align === "right" ? "right center" : "center";

  return (
    <div style={{ paddingTop, paddingLeft }} className={className}>
      <Image
        src="/pawpoint_header-removebg-preview.png"
        alt="PawPoint Logo"
        width={LOGO_WIDTH}
        height={height}
        draggable={false}
        priority
        style={{
          height: `${height}px`,
          width: "auto",
          objectFit: "contain",
          objectPosition,
        }}
      />
    </div>
  );
}
