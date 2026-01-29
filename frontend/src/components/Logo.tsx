import Image from "next/image";

// Change LOGO_HEIGHT to adjust logo size across entire site
const LOGO_HEIGHT = 180; // in pixels (h-16 = 64px)

// Aspect ratio based on actual image dimensions (280:62 ≈ 4.5:1)
const ASPECT_RATIO = 4.5;

// Change NAVBAR_HEIGHT to adjust navbar height across entire site
export const NAVBAR_HEIGHT = 100; // in pixels - controls the fixed navbar height

interface LogoProps {
  align?: "left" | "center" | "right";
  paddingTop?: string;
  paddingLeft?: string;
  className?: string;
  height?: number;
  width?: number;
  cropTop?: number;
  cropBottom?: number;
  cropLeft?: number;
  cropRight?: number;
}

export function Logo({
  align = "left",
  paddingTop = "20px",
  paddingLeft = "0px",
  className = "",
  height = LOGO_HEIGHT,
  width,
  cropTop = 0,
  cropBottom = 0,
  cropLeft = 0,
  cropRight = 0,
}: LogoProps = {}) {
  const objectPosition =
    align === "left" ? "left center" : align === "right" ? "right center" : "center";

  const calculatedWidth = width || height * ASPECT_RATIO;

  const hasCropping = cropTop || cropBottom || cropLeft || cropRight;

  return (
    <div style={{ paddingTop, paddingLeft }} className={className}>
      {hasCropping ? (
        <div
          style={{
            width: `${calculatedWidth - cropLeft - cropRight}px`,
            height: `${height - cropTop - cropBottom}px`,
            overflow: "hidden",
            position: "relative",
          }}
        >
          <Image
            src="/pawpoint_header-removebg-preview.png"
            alt="PawPoint Logo"
            width={calculatedWidth}
            height={height}
            draggable={false}
            priority
            style={{
              position: "absolute",
              top: `-${cropTop}px`,
              left: `-${cropLeft}px`,
              height: `${height}px`,
              width: width ? `${width}px` : "auto",
              objectFit: "contain",
              objectPosition,
            }}
          />
        </div>
      ) : (
        <Image
          src="/pawpoint_header-removebg-preview.png"
          alt="PawPoint Logo"
          width={calculatedWidth}
          height={height}
          draggable={false}
          priority
          style={{
            height: `${height}px`,
            width: width ? `${width}px` : "auto",
            objectFit: "contain",
            objectPosition,
          }}
        />
      )}
    </div>
  );
}
