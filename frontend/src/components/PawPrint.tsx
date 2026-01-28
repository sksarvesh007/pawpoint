import Image from "next/image";

interface PawPrintProps {
  className?: string;
  size?: number;
}

export const PawPrint = ({ className = "", size = 40 }: PawPrintProps) => (
  <Image
    src="/paws.png"
    alt="Paw print"
    width={size}
    height={size}
    className={className}
  />
);
