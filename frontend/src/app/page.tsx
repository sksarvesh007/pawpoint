import Link from "next/link";
import { Logo, NAVBAR_HEIGHT } from "@/components/Logo";

// Custom Icon Components
const PawLogo = Logo;

const PhoneIcon = () => (
  <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
    <circle cx="24" cy="24" r="22" fill="#FEF3E2" stroke="#F5A623" strokeWidth="2" />
    <circle cx="24" cy="24" r="16" fill="white" stroke="#3EB5B0" strokeWidth="2" />
    {/* Phone */}
    <path d="M18 16c0-1 .8-2 2-2h8c1.2 0 2 1 2 2v16c0 1-.8 2-2 2h-8c-1.2 0-2-1-2-2V16z" fill="#3EB5B0" />
    <rect x="20" y="18" width="8" height="10" rx="1" fill="white" />
    <circle cx="24" cy="31" r="1.5" fill="white" />
    {/* Clock indicator */}
    <circle cx="32" cy="14" r="6" fill="#F5A623" />
    <path d="M32 11v3l2 1" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
);

const ClipboardIcon = () => (
  <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
    <circle cx="24" cy="24" r="22" fill="#FEF3E2" stroke="#F5A623" strokeWidth="2" />
    {/* Clipboard */}
    <rect x="14" y="12" width="20" height="26" rx="2" fill="white" stroke="#3EB5B0" strokeWidth="2" />
    <rect x="18" y="10" width="12" height="4" rx="1" fill="#3EB5B0" />
    {/* Lines */}
    <line x1="18" y1="20" x2="30" y2="20" stroke="#3EB5B0" strokeWidth="2" />
    <line x1="18" y1="26" x2="30" y2="26" stroke="#3EB5B0" strokeWidth="2" />
    <line x1="18" y1="32" x2="26" y2="32" stroke="#3EB5B0" strokeWidth="2" />
  </svg>
);

const CalendarCheckIcon = () => (
  <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
    <circle cx="24" cy="24" r="22" fill="#E8F7F6" stroke="#3EB5B0" strokeWidth="2" />
    {/* Calendar */}
    <rect x="12" y="14" width="24" height="22" rx="2" fill="white" stroke="#3EB5B0" strokeWidth="2" />
    <line x1="12" y1="22" x2="36" y2="22" stroke="#3EB5B0" strokeWidth="2" />
    <rect x="16" y="10" width="3" height="6" rx="1" fill="#3EB5B0" />
    <rect x="29" y="10" width="3" height="6" rx="1" fill="#3EB5B0" />
    {/* Checkmark */}
    <path d="M18 28l4 4 8-8" stroke="#3EB5B0" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const DashboardIcon = () => (
  <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
    <circle cx="24" cy="24" r="22" fill="#E8F7F6" stroke="#3EB5B0" strokeWidth="2" />
    {/* Monitor */}
    <rect x="10" y="12" width="28" height="18" rx="2" fill="white" stroke="#3EB5B0" strokeWidth="2" />
    {/* Stand */}
    <path d="M20 30v4h8v-4" stroke="#3EB5B0" strokeWidth="2" />
    <line x1="16" y1="34" x2="32" y2="34" stroke="#3EB5B0" strokeWidth="2" />
    {/* Chart bars */}
    <rect x="14" y="22" width="4" height="6" fill="#F5A623" />
    <rect x="20" y="18" width="4" height="10" fill="#3EB5B0" />
    <rect x="26" y="20" width="4" height="8" fill="#F5A623" />
    <rect x="32" y="16" width="4" height="12" fill="#3EB5B0" />
  </svg>
);

const PawPrint = ({ className = "" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 100 100" fill="currentColor">
    <ellipse cx="50" cy="65" rx="25" ry="20" />
    <circle cx="30" cy="35" r="12" />
    <circle cx="70" cy="35" r="12" />
    <circle cx="20" cy="55" r="10" />
    <circle cx="80" cy="55" r="10" />
  </svg>
);

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-white overflow-x-hidden">
      {/* Header */}
      <header
        className="flex items-center justify-between px-20 bg-white relative z-20 border-b border-white"
        style={{ height: `${NAVBAR_HEIGHT}px` }}
      >
        <div className="flex items-center gap-2">
          <PawLogo />
        </div>
        <nav className="flex items-center gap-10">
          <Link
            href="#features"
            className="text-[17px] font-medium text-[#4A5568] hover:text-[#2A9D8F] transition-colors"
          >
            Features
          </Link>
          <Link
            href="#pricing"
            className="text-[17px] font-medium text-[#4A5568] hover:text-[#2A9D8F] transition-colors"
          >
            Pricing
          </Link>
          <Link
            href="#demo"
            className="text-[17px] font-medium text-[#4A5568] hover:text-[#2A9D8F] transition-colors"
          >
            Demo
          </Link>
          <Link
            href="/signup"
            className="px-8 py-3 text-[16px] font-bold text-white bg-[#3DA99F] rounded-lg hover:bg-[#2A9D8F] transition-all shadow-[0_4px_14px_0_rgba(61,169,159,0.3)]"
          >
            Request a Demo
          </Link>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="relative pt-20 overflow-visible">
        {/* Background Paw Prints */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.05]">
          <PawPrint className="absolute top-10 left-10 w-24 h-24 text-[#2A9D8F]" />
          <PawPrint className="absolute top-40 right-40 w-32 h-32 text-[#2A9D8F] rotate-[15deg]" />
          <PawPrint className="absolute top-20 left-[40%] w-12 h-12 text-[#2A9D8F] rotate-[-20deg]" />
          <PawPrint className="absolute bottom-40 left-20 w-16 h-16 text-[#2A9D8F]" />
        </div>

        {/* Hero Content */}
        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between px-20 gap-16">
          <div className="flex flex-col gap-8 max-w-[600px]">
            <h1 className="text-[64px] font-black text-[#1D3533] leading-[1.05] tracking-tight">
              The AI Receptionist
              <br />
              <span className="text-[#3DA99F]">for Veterinary Clinics</span>
            </h1>
            <p className="text-[22px] text-[#5C6F6C] leading-relaxed font-medium">
              Never miss a call. Capture more
              <br />
              appointments. Reduce staff stress.
            </p>
            <div className="flex gap-4 mt-2">
              <Link
                href="#demo"
                className="px-8 py-4 text-[18px] font-bold text-white bg-[#3DA99F] rounded-xl hover:bg-[#2A9D8F] transition-all shadow-[0_6px_20px_rgba(61,169,159,0.4)]"
              >
                See PawPoint in Action
              </Link>
              <Link
                href="/signup"
                className="px-8 py-4 text-[18px] font-bold text-[#2D3748] bg-white rounded-xl border-2 border-[#E2E8F0] hover:bg-gray-50 transition-all"
              >
                Request a Demo
              </Link>
            </div>
            <p className="text-[15px] font-bold text-[#718096] flex items-center gap-2">
              <span className="text-[#3DA99F] text-lg">▶</span> Setup in days • Flat monthly pricing
            </p>
          </div>

          {/* Phone Mockup Section */}
          <div className="relative flex flex-col items-center">
            {/* Soft Teal Blob Background */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[550px] h-[550px] bg-[#E0F2F1] rounded-full blur-[80px] opacity-70 pointer-events-none -z-10"></div>

            {/* Ringing Arcs */}
            <div className="absolute top-[20%] -left-12 opacity-40 animate-pulse">
              <svg width="60" height="120" viewBox="0 0 60 120" fill="none">
                <path d="M50 10C30 30 30 90 50 110" stroke="#F4A261" strokeWidth="4" strokeLinecap="round" />
                <path d="M30 30C15 45 15 75 30 90" stroke="#F4A261" strokeWidth="4" strokeLinecap="round" opacity="0.6" />
              </svg>
            </div>
            <div className="absolute top-[20%] -right-12 opacity-40 animate-pulse">
              <svg width="60" height="120" viewBox="0 0 60 120" fill="none">
                <path d="M10 10C30 30 30 90 10 110" stroke="#F4A261" strokeWidth="4" strokeLinecap="round" />
                <path d="M30 30C45 45 45 75 30 90" stroke="#F4A261" strokeWidth="4" strokeLinecap="round" opacity="0.6" />
              </svg>
            </div>

            {/* iPhone Frame */}
            <div className="relative w-[280px] h-[580px] bg-[#2D3436] rounded-[50px] p-[12px] shadow-[0_45px_90px_rgba(0,0,0,0.2)] rotate-[6deg] transition-all hover:rotate-[4deg] duration-500">
              {/* Screen Content */}
              <div className="relative w-full h-full bg-[#3DA99F] rounded-[40px] overflow-hidden flex flex-col items-center">
                {/* Dynamic Island */}
                <div className="absolute top-3 left-1/2 -translate-x-1/2 w-[90px] h-[26px] bg-black rounded-full z-20"></div>

                {/* Content Area */}
                <div className="w-full h-full flex flex-col items-center pt-14 px-6 gap-4">
                  {/* Status Bar */}
                  <div className="absolute top-1.5 left-0 right-0 flex justify-between px-8 text-[11px] text-white/90 font-bold">
                    <span>9:41</span>
                    <div className="flex gap-1.5 items-center">
                      <svg width="18" height="12" viewBox="0 0 18 12" fill="currentColor"><path d="M14 1h-1V0H3v1H2v2H1v2H0v2h1v2h1v2h1v1h11v-1h1v-2h1v-2h1V5h-1V3h-1V1zM3 10V2h10v8H3z" /></svg>
                    </div>
                  </div>

                  {/* Avatar */}
                  <div className="w-20 h-20 bg-[#F4A261] rounded-full flex items-center justify-center shadow-xl ring-4 ring-white/20 mt-4">
                    <svg width="44" height="44" viewBox="0 0 100 100" fill="white">
                      <ellipse cx="50" cy="62" rx="22" ry="16" /><circle cx="32" cy="40" r="10" /><circle cx="68" cy="40" r="10" /><circle cx="22" cy="55" r="8" /><circle cx="78" cy="55" r="8" />
                    </svg>
                  </div>

                  {/* Identity */}
                  <div className="text-center">
                    <h2 className="text-[22px] font-bold text-white tracking-tight">PawPoint AI</h2>
                    <p className="text-[14px] text-white/80 font-medium h-4">answering...</p>
                  </div>

                  {/* Message Bubble 1 */}
                  <div className="bg-white rounded-[24px] px-6 py-5 w-full shadow-lg mt-4 h-[120px] flex items-center">
                    <p className="text-[15px] text-[#2D3748] leading-relaxed font-bold">
                      Hi Thanks for calling.<br />
                      How can we assist you and your pet today?
                    </p>
                  </div>

                  {/* Appointment Box */}
                  <div className="bg-white rounded-[20px] px-6 py-4 w-full shadow-lg flex items-center justify-between mt-2">
                    <span className="text-[14px] font-bold text-[#2D3748] leading-tight flex-1">
                      Appointment Request<br />Captured
                    </span>
                    <div className="w-6 h-6 rounded-full bg-[#E0F2F1] flex items-center justify-center ml-2">
                      <span className="text-[#3DA99F] text-sm font-black">✓</span>
                    </div>
                  </div>

                  {/* Mic Control */}
                  <div className="mt-auto mb-8">
                    <div className="w-16 h-16 bg-[#F4A261] rounded-full flex items-center justify-center shadow-lg ring-4 ring-white/20 animate-bounce">
                      <svg width="28" height="28" viewBox="0 0 24 24" fill="white">
                        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" /><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
                      </svg>
                    </div>
                  </div>

                  {/* Home Bar */}
                  <div className="w-32 h-1.5 bg-white/30 rounded-full mb-3"></div>
                </div>
              </div>
            </div>

            {/* Tap to hear text */}
            <div className="mt-12 text-center">
              <p className="text-[18px] font-bold text-[#4A5568] flex items-center gap-3">
                Tap to hear PawPoint answer a call <span className="text-3xl animate-bounce">🐾🎧</span>
              </p>
            </div>
          </div>
        </div>

        {/* Wave section - Text Removed */}
        <div className="relative -mt-4">
          <svg viewBox="0 0 1440 200" className="w-full block" preserveAspectRatio="none" style={{ height: '160px' }}>
            <path fill="#C5E8E6" fillOpacity="0.5" d="M0,100 C200,140 400,80 600,100 C800,120 1000,60 1200,100 C1300,120 1400,100 1440,90 L1440,200 L0,200 Z"></path>
            <path fill="#9DD9D5" fillOpacity="0.6" d="M0,120 C200,150 400,100 600,130 C800,160 1000,100 1200,140 C1350,160 1400,140 1440,130 L1440,200 L0,200 Z"></path>
            <path fill="#7ECDC8" fillOpacity="0.7" d="M0,150 C200,170 400,140 600,160 C800,180 1000,140 1200,170 C1350,185 1420,170 1440,160 L1440,200 L0,200 Z"></path>
          </svg>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="relative bg-white py-20 px-20">
        <div className="flex justify-center gap-6 relative z-10">
          {/* Feature 1 */}
          <div className="w-[280px] p-8 bg-[#FFF9F0] rounded-[24px] flex flex-col gap-4 shadow-sm border border-orange-100/50">
            <PhoneIcon />
            <h3 className="text-[19px] font-black text-[#1D3533] leading-tight">
              24/7 Call<br />Coverage
            </h3>
            <p className="text-[15px] text-[#5C6F6C] font-medium">
              Never miss a pet parent in need.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="w-[280px] p-8 bg-[#FFF9F0] rounded-[24px] flex flex-col gap-4 shadow-sm border border-orange-100/50">
            <ClipboardIcon />
            <h3 className="text-[19px] font-black text-[#1D3533] leading-tight">
              Never Miss<br />an Appointment
            </h3>
            <p className="text-[15px] text-[#5C6F6C] font-medium">
              Recover lost revenue from missed calls.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="w-[280px] p-8 bg-[#FFF9F0] rounded-[24px] flex flex-col gap-4 shadow-sm border border-orange-100/50">
            <CalendarCheckIcon />
            <h3 className="text-[19px] font-black text-[#3DA99F] leading-tight">
              Appointment<br />Requests Captured
            </h3>
            <p className="text-[15px] text-[#5C6F6C] font-medium">
              Capture calls when your team is busy or gone for.
            </p>
          </div>

          {/* Feature 4 */}
          <div className="w-[280px] p-8 bg-[#E0F2F1]/50 rounded-[24px] flex flex-col gap-4 shadow-sm border border-teal-100/50">
            <DashboardIcon />
            <h3 className="text-[19px] font-black text-[#1D3533] leading-tight">
              Staff<br />Dashboard Alerts
            </h3>
            <p className="text-[15px] text-[#5C6F6C] font-medium">
              Smart. HIPAA conscious, and easy to use.
            </p>
          </div>
        </div>
      </section>

      {/* Large Feature Cards */}
      <section className="px-20 py-12 bg-white relative">
        <div className="flex justify-center gap-8 relative z-10">
          {/* Large Card 1 */}
          <div className="w-[580px] p-8 bg-white rounded-[24px] border border-gray-100 flex items-center gap-6 shadow-[0_10px_30px_rgba(0,0,0,0.04)]">
            <PhoneIcon />
            <div className="flex flex-col gap-1">
              <h3 className="text-xl font-black text-[#1D3533]">
                24/7 Call Coverage
              </h3>
              <p className="text-[16px] text-[#5C6F6C] font-medium">
                Never miss a pet parent in need.
              </p>
            </div>
          </div>

          {/* Large Card 2 */}
          <div className="w-[580px] p-8 bg-white rounded-[24px] border border-gray-100 flex items-center gap-6 shadow-[0_10px_30px_rgba(0,0,0,0.04)]">
            <CalendarCheckIcon />
            <div className="flex flex-col gap-1">
              <h3 className="text-xl font-black text-[#1D3533]">
                After-Hours & Overflow Support
              </h3>
              <p className="text-[16px] text-[#5C6F6C] font-medium">
                Capture calls when your team is busy or gone for the day.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section id="demo" className="relative">
        {/* Top Wave Layers */}
        <div className="relative">
          <svg viewBox="0 0 1440 200" className="w-full block" preserveAspectRatio="none" style={{ height: '100px' }}>
            <path fill="#F5F7F4" d="M0,0 L1440,0 L1440,60 C1200,90 1000,50 800,70 C600,90 400,50 200,70 C100,80 50,70 0,60 Z"></path>
            <path fill="#C5E8E6" fillOpacity="0.5" d="M0,50 C200,80 400,40 600,60 C800,80 1000,40 1200,70 C1350,85 1420,75 1440,70 L1440,200 L0,200 Z"></path>
            <path fill="#8DD4CF" fillOpacity="0.6" d="M0,80 C200,100 400,70 600,90 C800,110 1000,70 1200,100 C1350,115 1420,100 1440,95 L1440,200 L0,200 Z"></path>
            <path fill="#3EB5B0" d="M0,110 C200,130 400,100 600,120 C800,140 1000,100 1200,130 C1350,145 1420,130 1440,120 L1440,200 L0,200 Z"></path>
          </svg>
        </div>

        {/* CTA Content */}
        <div className="bg-[#3DA99F] relative overflow-hidden">
          {/* Decorative Elements */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.08]">
            <PawPrint className="absolute top-10 left-20 w-32 h-32 text-white" />
            <PawPrint className="absolute bottom-10 right-20 w-40 h-40 text-white rotate-[25deg]" />
          </div>

          <div className="px-20 py-24 flex flex-col items-center gap-8 relative z-10">
            <h2 className="text-[52px] font-black text-white text-center leading-tight">
              Ready to Never Miss a Call?
            </h2>
            <p className="text-[20px] text-white/90 text-center max-w-2xl font-medium">
              See how PawPoint helps clinics capture more appointments with less effort.
            </p>
            <div className="flex gap-6 mt-4">
              <Link
                href="/signup"
                className="px-10 py-5 text-[18px] font-black text-white bg-[#F4A261] rounded-xl hover:bg-[#E78B45] transition-all shadow-[0_8px_25px_rgba(244,162,97,0.4)] hover:shadow-[0_12px_30px_rgba(244,162,97,0.5)]"
              >
                Test the AI
              </Link>
              <Link
                href="/signup"
                className="px-10 py-5 text-[18px] font-black text-[#1D3533] bg-white rounded-xl hover:bg-gray-50 transition-all shadow-lg"
              >
                Book a Demo
              </Link>
            </div>
          </div>
        </div>

        {/* Bottom Wave Layers */}
        <div className="relative bg-[#3EB5B0]">
          <svg viewBox="0 0 1440 200" className="w-full block" preserveAspectRatio="none" style={{ height: '100px' }}>
            <path fill="#3EB5B0" d="M0,0 L1440,0 L1440,40 L0,40 Z"></path>
            <path fill="#5AC4C0" d="M0,30 C200,50 400,20 600,40 C800,60 1000,20 1200,50 C1350,65 1420,50 1440,45 L1440,200 L0,200 Z"></path>
            <path fill="#8DD4CF" fillOpacity="0.8" d="M0,60 C200,80 400,50 600,70 C800,90 1000,50 1200,80 C1350,95 1420,80 1440,75 L1440,200 L0,200 Z"></path>
            <path fill="#F5F7F4" d="M0,90 C200,110 400,80 600,100 C800,120 1000,80 1200,110 C1350,125 1420,110 1440,105 L1440,200 L0,200 Z"></path>
          </svg>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-100">
        <div className="px-20 py-16">
          <div className="flex flex-col md:flex-row justify-between items-start gap-12">
            {/* Logo and tagline */}
            <div className="flex flex-col items-start gap-6 max-w-[300px]">
              <div className="flex items-center gap-2">
                <PawLogo />
              </div>
              <p className="text-[15px] text-[#5C6F6C] font-medium leading-relaxed">
                The #1 AI Receptionist tool built exclusively for veterinary practices.
              </p>
              {/* Social Icons */}
              <div className="flex gap-4 mt-2">
                <Link href="#" className="p-2 bg-gray-50 rounded-full text-[#2D3748] hover:text-[#2A9D8F] transition-all hover:scale-110">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
                  </svg>
                </Link>
                <Link href="#" className="p-2 bg-gray-50 rounded-full text-[#2D3748] hover:text-[#2A9D8F] transition-all hover:scale-110">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                  </svg>
                </Link>
                <Link href="#" className="p-2 bg-gray-50 rounded-full text-[#2D3748] hover:text-[#2A9D8F] transition-all hover:scale-110">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                  </svg>
                </Link>
                <Link href="#" className="p-2 bg-gray-50 rounded-full text-[#2D3748] hover:text-[#2A9D8F] transition-all hover:scale-110">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z" />
                  </svg>
                </Link>
              </div>
            </div>

            {/* Links */}
            <div className="flex flex-wrap gap-16 md:gap-24">
              <div className="flex flex-col gap-5">
                <h4 className="font-bold text-[#1D3533] text-[16px] uppercase tracking-wider">Product</h4>
                <div className="flex flex-col gap-3">
                  <Link href="/" className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors">Home</Link>
                  <Link href="#features" className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors">Features</Link>
                  <Link href="#pricing" className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors">Pricing</Link>
                  <Link href="#demo" className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors">Request a Demo</Link>
                </div>
              </div>

              <div className="flex flex-col gap-5">
                <h4 className="font-bold text-[#1D3533] text-[16px] uppercase tracking-wider">Why PawPoint</h4>
                <div className="flex flex-col gap-3">
                  <Link href="#" className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors">About Us</Link>
                  <Link href="#" className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors">FAQ</Link>
                  <Link href="#" className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors">Contact</Link>
                </div>
              </div>

              <div className="flex flex-col gap-5">
                <h4 className="font-bold text-[#1D3533] text-[16px] uppercase tracking-wider">Company</h4>
                <div className="flex flex-col gap-3">
                  <Link href="#" className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors">Terms of Service</Link>
                  <Link href="#" className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors">Privacy Policy</Link>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-16 pt-8 border-t border-gray-50 flex justify-between items-center text-[14px] text-gray-400 font-medium">
            <p>© 2026 PawPoint AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
