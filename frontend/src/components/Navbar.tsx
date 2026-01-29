"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Logo, NAVBAR_HEIGHT } from "@/components/Logo";

interface NavItem {
  href: string;
  label: string;
  isHashLink?: boolean;
}

const navItems: NavItem[] = [
  { href: "/#features", label: "Features", isHashLink: true },
  { href: "/faq", label: "FAQ" },
  { href: "/#pricing", label: "Pricing", isHashLink: true },
  { href: "/demo", label: "Demo" },
  { href: "/about", label: "About Us" },
];

export function Navbar() {
  const pathname = usePathname();

  const isActive = (item: NavItem) => {
    if (item.isHashLink) {
      return false;
    }
    // Match exact path or if pathname starts with item.href for nested routes
    return pathname === item.href || pathname.startsWith(item.href + "/");
  };

  return (
    <header
      className="flex items-center justify-between px-20 bg-white sticky top-0 z-50 border-b border-zinc-100 shadow-sm"
      style={{ height: `${NAVBAR_HEIGHT}px` }}
    >
      <div className="flex items-center gap-2">
        <Link href="/">
          <Logo />
        </Link>
      </div>
      <nav className="flex items-center gap-8">
        {navItems.map((item) => {
          const active = isActive(item);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`relative text-[17px] font-medium transition-colors px-4 py-2 rounded-full ${
                active
                  ? "text-[#2A9D8F] bg-[#E0F2F1]"
                  : "text-[#4A5568] hover:text-[#2A9D8F]"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
        <Link
          href="/login"
          className="px-6 py-3 text-[16px] font-bold text-[#3DA99F] border-2 border-[#3DA99F] rounded-lg hover:bg-[#E0F2F1] transition-all"
        >
          Login as Hospital
        </Link>
        <Link
          href="/signup"
          className="px-6 py-3 text-[16px] font-bold text-white bg-[#3DA99F] rounded-lg hover:bg-[#2A9D8F] transition-all shadow-[0_4px_14px_0_rgba(61,169,159,0.3)]"
        >
          Signup as Hospital
        </Link>
      </nav>
    </header>
  );
}
