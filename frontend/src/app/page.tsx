"use client";

import { useState } from "react";
import Link from "next/link";
import { X } from "lucide-react";
import { Logo } from "@/components/Logo";
import { PawBackground } from "@/components/PawBackground";
import { PawPrint } from "@/components/PawPrint";
import { FAQAccordion } from "@/components/FAQAccordion";
import { Navbar } from "@/components/Navbar";

const PawLogo = Logo;

const PhoneIcon = () => (
  <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
    {/* Phone */}
    <path
      d="M18 16c0-1 .8-2 2-2h8c1.2 0 2 1 2 2v16c0 1-.8 2-2 2h-8c-1.2 0-2-1-2-2V16z"
      fill="#3EB5B0"
    />
    <rect x="20" y="18" width="8" height="10" rx="1" fill="white" />
    <circle cx="24" cy="31" r="1.5" fill="white" />
    {/* Clock indicator */}
    <circle cx="32" cy="14" r="6" fill="#F5A623" />
    <path
      d="M32 11v3l2 1"
      stroke="white"
      strokeWidth="1.5"
      strokeLinecap="round"
    />
  </svg>
);

const ClipboardIcon = () => (
  <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
    {/* Clipboard */}
    <rect
      x="14"
      y="12"
      width="20"
      height="26"
      rx="2"
      fill="white"
      stroke="#3EB5B0"
      strokeWidth="2"
    />
    <rect x="18" y="10" width="12" height="4" rx="1" fill="#3EB5B0" />
    {/* Lines */}
    <line x1="18" y1="20" x2="30" y2="20" stroke="#3EB5B0" strokeWidth="2" />
    <line x1="18" y1="26" x2="30" y2="26" stroke="#3EB5B0" strokeWidth="2" />
    <line x1="18" y1="32" x2="26" y2="32" stroke="#3EB5B0" strokeWidth="2" />
  </svg>
);

const CalendarCheckIcon = () => (
  <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
    {/* Calendar */}
    <rect
      x="12"
      y="14"
      width="24"
      height="22"
      rx="2"
      fill="white"
      stroke="#3EB5B0"
      strokeWidth="2"
    />
    <line x1="12" y1="22" x2="36" y2="22" stroke="#3EB5B0" strokeWidth="2" />
    <rect x="16" y="10" width="3" height="6" rx="1" fill="#3EB5B0" />
    <rect x="29" y="10" width="3" height="6" rx="1" fill="#3EB5B0" />
    {/* Checkmark */}
    <path
      d="M18 28l4 4 8-8"
      stroke="#3EB5B0"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const DashboardIcon = () => (
  <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
    {/* Monitor */}
    <rect
      x="10"
      y="12"
      width="28"
      height="18"
      rx="2"
      fill="white"
      stroke="#3EB5B0"
      strokeWidth="2"
    />
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

export default function Home() {
  const [showContactForm, setShowContactForm] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    clinicName: "",
    phone: "",
  });
  const [formSubmitted, setFormSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, this would send the data to a backend
    console.log("Form submitted:", formData);
    setFormSubmitted(true);
    setTimeout(() => {
      setShowContactForm(false);
      setFormSubmitted(false);
      setFormData({ name: "", email: "", clinicName: "", phone: "" });
    }, 2000);
  };

  return (
    <div className="flex min-h-screen flex-col bg-white">
      {/* Header */}
      <Navbar />

      {/* Hero Section */}
      <section className="relative pt-20 overflow-visible">
        {/* Background Paw Prints - biased towards edges */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.04]">
          <PawPrint
            size={50}
            className="absolute top-10 left-6 rotate-[15deg]"
          />
          <PawPrint
            size={60}
            className="absolute top-40 right-8 rotate-[-25deg]"
          />
          <PawPrint
            size={35}
            className="absolute top-20 left-[8%] rotate-[45deg]"
          />
          <PawPrint
            size={45}
            className="absolute bottom-40 left-12 rotate-[-15deg]"
          />
          <PawPrint
            size={40}
            className="absolute top-60 right-[5%] rotate-[30deg]"
          />
          <PawPrint
            size={55}
            className="absolute bottom-60 right-6 rotate-[-40deg]"
          />
          <PawPrint
            size={42}
            className="absolute top-[30%] left-[3%] rotate-[20deg]"
          />
          <PawPrint
            size={48}
            className="absolute bottom-20 right-[7%] rotate-[-35deg]"
          />
        </div>

        {/* Decorative Ovals Background - positioned behind waves, near phone */}
        <div className="absolute right-[5%] top-0 w-[500px] h-[150%] pointer-events-none z-[5] overflow-visible">
          {/* Additional decorative circles/ovals - clustered around phone */}
          <div className="absolute top-[10%] left-[10%] w-[180px] h-[220px] bg-[#7ECDC8]/30 rounded-[50%]"></div>
          <div className="absolute top-[25%] right-[5%] w-[160px] h-[160px] bg-[#3DA99F]/25 rounded-full"></div>
          <div className="absolute top-[20%] right-[-10%] w-[220px] h-[180px] bg-[#2A9D8F]/20 rounded-[50%] rotate-[20deg]"></div>
        </div>

        {/* Hero Content */}
        <div className="relative z-[25] flex flex-col md:flex-row items-start justify-between px-20 gap-16">
          <div className="flex flex-col gap-8 max-w-[600px]">
            <h1 className="text-[64px] font-nunito font-black text-[#1D3533] leading-[1.05] tracking-tight">
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
                href="/demo"
                className="px-8 py-4 text-[18px] font-bold text-white bg-[#3DA99F] rounded-xl hover:bg-[#2A9D8F] transition-all shadow-[0_6px_20px_rgba(61,169,159,0.4)]"
              >
                See PawPoint in Action
              </Link>
              <button
                onClick={() => setShowContactForm(true)}
                className="px-8 py-4 text-[18px] font-bold text-white bg-[#F5A623] rounded-xl hover:bg-[#E09000] transition-all shadow-[0_6px_20px_rgba(245,166,35,0.4)]"
              >
                Request a Demo
              </button>
            </div>
            <p className="text-[15px] font-bold text-[#718096] flex items-center gap-2">
              <span className="text-[#3DA99F] text-lg">▶</span> Setup in days •
              Flat monthly pricing
            </p>
          </div>

          {/* Phone Mockup Section */}
          <div
            className="relative flex flex-col items-center"
            style={{ overflow: "visible" }}
          >
            {/* Paw Background without circles */}
            <PawBackground
              pawCount={6}
              circleCount={0}
              pawOpacity={0.12}
              circleOpacity={0}
              pawSizeRange={[40, 70]}
              circleSizeRange={[0, 0]}
              className="w-[600px] h-[650px] absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-[5] overflow-visible"
            />

            {/* Ringing Arcs */}
            <div className="absolute top-[20%] -left-12 opacity-40 animate-pulse z-[30]">
              <svg width="60" height="120" viewBox="0 0 60 120" fill="none">
                <path
                  d="M50 10C30 30 30 90 50 110"
                  stroke="#F4A261"
                  strokeWidth="4"
                  strokeLinecap="round"
                />
                <path
                  d="M30 30C15 45 15 75 30 90"
                  stroke="#F4A261"
                  strokeWidth="4"
                  strokeLinecap="round"
                  opacity="0.6"
                />
              </svg>
            </div>
            <div className="absolute top-[20%] -right-12 opacity-40 animate-pulse z-[30]">
              <svg width="60" height="120" viewBox="0 0 60 120" fill="none">
                <path
                  d="M10 10C30 30 30 90 10 110"
                  stroke="#F4A261"
                  strokeWidth="4"
                  strokeLinecap="round"
                />
                <path
                  d="M30 30C45 45 45 75 30 90"
                  stroke="#F4A261"
                  strokeWidth="4"
                  strokeLinecap="round"
                  opacity="0.6"
                />
              </svg>
            </div>

            {/* iPhone Frame */}
            <div className="relative w-[280px] h-[580px] bg-[#2D3436] rounded-[50px] p-[12px] shadow-[0_45px_90px_rgba(0,0,0,0.2)] rotate-[6deg] transition-all hover:rotate-0 duration-500 z-[30]">
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
                      <svg
                        width="18"
                        height="12"
                        viewBox="0 0 18 12"
                        fill="currentColor"
                      >
                        <path d="M14 1h-1V0H3v1H2v2H1v2H0v2h1v2h1v2h1v1h11v-1h1v-2h1v-2h1V5h-1V3h-1V1zM3 10V2h10v8H3z" />
                      </svg>
                    </div>
                  </div>

                  {/* Avatar */}
                  <div className="w-20 h-20 bg-[#F4A261] rounded-full flex items-center justify-center shadow-xl ring-4 ring-white/20 mt-4">
                    <svg
                      width="44"
                      height="44"
                      viewBox="0 0 100 100"
                      fill="white"
                    >
                      <ellipse cx="50" cy="62" rx="22" ry="16" />
                      <circle cx="32" cy="40" r="10" />
                      <circle cx="68" cy="40" r="10" />
                      <circle cx="22" cy="55" r="8" />
                      <circle cx="78" cy="55" r="8" />
                    </svg>
                  </div>

                  {/* Identity */}
                  <div className="text-center">
                    <h2 className="text-[22px] font-nunito font-bold text-white tracking-tight">
                      PawPoint AI
                    </h2>
                    <p className="text-[14px] text-white/80 font-medium h-4">
                      answering...
                    </p>
                  </div>

                  {/* Message Bubble 1 */}
                  <div className="bg-white rounded-[24px] px-6 py-5 w-full shadow-lg mt-4 h-[120px] flex items-center">
                    <p className="text-[15px] text-[#2D3748] leading-relaxed font-bold">
                      Hi Thanks for calling.
                      <br />
                      How can we assist you and your pet today?
                    </p>
                  </div>

                  {/* Appointment Box */}
                  <div className="bg-white rounded-[20px] px-6 py-4 w-full shadow-lg flex items-center justify-between mt-2">
                    <span className="text-[14px] font-bold text-[#2D3748] leading-tight flex-1">
                      Appointment Request
                      <br />
                      Captured
                    </span>
                    <div className="w-6 h-6 rounded-full bg-[#E0F2F1] flex items-center justify-center ml-2">
                      <span className="text-[#3DA99F] text-sm font-black">
                        ✓
                      </span>
                    </div>
                  </div>

                  {/* Mic Control */}
                  <div className="mt-auto mb-8">
                    <div className="w-16 h-16 bg-[#F4A261] rounded-full flex items-center justify-center shadow-lg ring-4 ring-white/20 animate-bounce">
                      <svg
                        width="28"
                        height="28"
                        viewBox="0 0 24 24"
                        fill="white"
                      >
                        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
                        <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
                      </svg>
                    </div>
                  </div>

                  {/* Home Bar */}
                  <div className="w-32 h-1.5 bg-white/30 rounded-full mb-3"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Wave section - Text Removed */}
        <div className="relative z-[15] -mt-[160px] pb-[260px]">
          {/* Paw prints over waves */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.04] z-10">
            <PawPrint
              size={30}
              className="absolute top-8 left-[15%] rotate-[25deg]"
            />
            <PawPrint
              size={35}
              className="absolute top-16 right-[25%] rotate-[-20deg]"
            />
            <PawPrint
              size={25}
              className="absolute bottom-10 left-[40%] rotate-[15deg]"
            />
            <PawPrint
              size={40}
              className="absolute top-12 right-[60%] rotate-[-35deg]"
            />
            <PawPrint
              size={28}
              className="absolute bottom-6 right-[10%] rotate-[40deg]"
            />
          </div>
          <svg
            width="100%"
            height="160"
            viewBox="0 0 1440 690"
            xmlns="http://www.w3.org/2000/svg"
            className="transition duration-300 ease-in-out delay-150"
            preserveAspectRatio="none"
          >
            <path
              d="M 0,700 L 0,356 C 67.66923076923078,398.87051282051283 135.33846153846156,441.74102564102566 217,413 C 298.66153846153844,384.25897435897434 394.3153846153846,283.90641025641025 485,231 C 575.6846153846154,178.09358974358975 661.4000000000001,172.63333333333333 743,178 C 824.5999999999999,183.36666666666667 902.0846153846153,199.56025641025641 978,183 C 1053.9153846153847,166.43974358974359 1128.2615384615385,117.12564102564102 1205,78 C 1281.7384615384615,38.87435897435898 1360.8692307692309,9.937179487179488 1440,-19 L 1440,700 L 0,700 Z"
              stroke="none"
              strokeWidth="0"
              fill="#7ECDC8"
              fillOpacity="1"
              className="transition-all duration-300 ease-in-out delay-150"
            ></path>
            <path
              d="M 0,700 L 0,706 C 67.15128205128207,715.6628205128204 134.30256410256413,725.325641025641 221,697 C 307.69743589743587,668.674358974359 413.9410256410257,602.3602564102564 487,578 C 560.0589743589743,553.6397435897436 599.9333333333333,571.2333333333333 676,563 C 752.0666666666667,554.7666666666667 864.3256410256411,520.7064102564103 947,491 C 1029.674358974359,461.2935897435897 1082.7641025641026,435.94102564102565 1160,410 C 1237.2358974358974,384.05897435897435 1338.6179487179488,357.5294871794872 1440,331 L 1440,700 L 0,700 Z"
              stroke="none"
              strokeWidth="0"
              fill="#2A9D8F"
              fillOpacity="1"
              className="transition-all duration-300 ease-in-out delay-150"
            ></path>
          </svg>
        </div>
      </section>

      {/* Wave above Features */}
      <div className="relative -mt-[260px]">
        <svg
          width="100%"
          height="200"
          id="svg"
          viewBox="0 0 1440 590"
          xmlns="http://www.w3.org/2000/svg"
          className="transition duration-300 ease-in-out delay-150"
          preserveAspectRatio="none"
        >
          <path
            d="M 0,600 L 0,112 C 108.06698564593302,121.67464114832535 216.13397129186603,131.3492822966507 327,124 C 437.86602870813397,116.65071770334929 551.5311004784689,92.2775119617225 627,86 C 702.4688995215311,79.7224880382775 739.7416267942583,91.54066985645933 816,95 C 892.2583732057417,98.45933014354067 1007.5023923444978,93.5598086124402 1118,95 C 1228.4976076555022,96.4401913875598 1334.248803827751,104.22009569377991 1440,112 L 1440,600 L 0,600 Z"
            stroke="none"
            strokeWidth="0"
            fill="#36bda5ff"
            fillOpacity="1"
            className="transition-all duration-300 ease-in-out delay-150 path-0"
            transform="rotate(-180 720 300)"
          />
          <path
            d="M 0,600 L 0,262 C 76.79425837320574,271.27272727272725 153.58851674641147,280.54545454545456 246,266 C 338.41148325358853,251.45454545454544 446.4401913875598,213.09090909090907 561,224 C 675.5598086124402,234.90909090909093 796.6507177033494,295.0909090909091 906,300 C 1015.3492822966506,304.9090909090909 1112.956937799043,254.54545454545456 1200,239 C 1287.043062200957,223.45454545454544 1363.5215311004786,242.72727272727272 1440,262 L 1440,600 L 0,600 Z"
            stroke="none"
            strokeWidth="0"
            fill="#7ECDC8"
            fillOpacity="1"
            className="transition-all duration-300 ease-in-out delay-150 path-1"
            transform="rotate(-180 720 300)"
          />
          <path
            d="M 0,600 L 0,412 C 124.83253588516749,402.3732057416268 249.66507177033498,392.7464114832536 337,405 C 424.334928229665,417.2535885167464 474.17224880382776,451.3875598086125 553,462 C 631.8277511961722,472.6124401913875 739.6459330143541,459.70334928229664 835,451 C 930.3540669856459,442.29665071770336 1013.2440191387561,437.79904306220095 1112,432 C 1210.7559808612439,426.20095693779905 1325.377990430622,419.1004784688995 1440,412 L 1440,600 L 0,600 Z"
            stroke="none"
            strokeWidth="0"
            fill="#2A9D8F"
            fillOpacity="1"
            className="transition-all duration-300 ease-in-out delay-150 path-2"
            transform="rotate(-180 720 300)"
          />
        </svg>
      </div>

      {/* Features Grid */}
      <section id="features" className="relative bg-white py-20 px-20">
        <div className="flex justify-center gap-6 relative z-10">
          {/* Feature 1 */}
          <div className="w-[280px] p-8 bg-[#FFF9F0] rounded-[24px] flex flex-col gap-4 shadow-sm border border-orange-100/50">
            <PhoneIcon />
            <h3 className="text-[19px] font-nunito font-black text-[#1D3533] leading-tight">
              24/7 Call
              <br />
              Coverage
            </h3>
            <p className="text-[15px] text-[#5C6F6C] font-medium">
              Never miss a pet parent in need.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="w-[280px] p-8 bg-[#FFF9F0] rounded-[24px] flex flex-col gap-4 shadow-sm border border-orange-100/50">
            <ClipboardIcon />
            <h3 className="text-[19px] font-nunito font-black text-[#1D3533] leading-tight">
              Never Miss
              <br />
              an Appointment
            </h3>
            <p className="text-[15px] text-[#5C6F6C] font-medium">
              Recover lost revenue from missed calls.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="w-[280px] p-8 bg-[#FFF9F0] rounded-[24px] flex flex-col gap-4 shadow-sm border border-orange-100/50">
            <CalendarCheckIcon />
            <h3 className="text-[19px] font-nunito font-black text-[#1D3533] leading-tight">
              Appointment
              <br />
              Requests Captured
            </h3>
            <p className="text-[15px] text-[#5C6F6C] font-medium">
              Capture calls when your team is busy or gone for.
            </p>
          </div>

          {/* Feature 4 */}
          <div className="w-[280px] p-8 bg-[#FFF9F0] rounded-[24px] flex flex-col gap-4 shadow-sm border border-orange-100/50">
            <DashboardIcon />
            <h3 className="text-[19px] font-nunito font-black text-[#1D3533] leading-tight">
              Staff
              <br />
              Dashboard Alerts
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
              <h3 className="text-xl font-nunito font-black text-[#1D3533]">
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
              <h3 className="text-xl font-nunito font-black text-[#1D3533]">
                After-Hours & Overflow Support
              </h3>
              <p className="text-[16px] text-[#5C6F6C] font-medium">
                Capture calls when your team is busy or gone for the day.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Wave Transition to FAQ */}
      <div className="relative">
        {/* Paw prints over waves */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.04] z-10">
          <PawPrint
            size={30}
            className="absolute top-8 left-[15%] rotate-[25deg]"
          />
          <PawPrint
            size={35}
            className="absolute top-16 right-[25%] rotate-[-20deg]"
          />
          <PawPrint
            size={28}
            className="absolute bottom-10 left-[40%] rotate-[15deg]"
          />
        </div>
        <svg
          width="100%"
          height="120"
          viewBox="0 0 1440 320"
          xmlns="http://www.w3.org/2000/svg"
          className="transition duration-300 ease-in-out delay-150"
          preserveAspectRatio="none"
        >
          <defs>
            <linearGradient
              id="faqWaveGradient1"
              x1="0%"
              y1="50%"
              x2="100%"
              y2="50%"
            >
              <stop offset="5%" stopColor="#7ECDC8"></stop>
              <stop offset="95%" stopColor="#B4E2DF"></stop>
            </linearGradient>
          </defs>
          <path
            d="M0,160L48,170.7C96,181,192,203,288,192C384,181,480,139,576,128C672,117,768,139,864,144C960,149,1056,139,1152,128C1248,117,1344,107,1392,101.3L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
            fill="url(#faqWaveGradient1)"
            fillOpacity="0.3"
          />
          <defs>
            <linearGradient
              id="faqWaveGradient2"
              x1="0%"
              y1="50%"
              x2="100%"
              y2="50%"
            >
              <stop offset="5%" stopColor="#7ECDC8"></stop>
              <stop offset="95%" stopColor="#A8DCD9"></stop>
            </linearGradient>
          </defs>
          <path
            d="M0,224L48,213.3C96,203,192,181,288,181.3C384,181,480,203,576,208C672,213,768,203,864,186.7C960,171,1056,149,1152,154.7C1248,160,1344,192,1392,208L1440,224L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
            fill="url(#faqWaveGradient2)"
            fillOpacity="0.5"
          />
          <defs>
            <linearGradient
              id="faqWaveGradient3"
              x1="0%"
              y1="50%"
              x2="100%"
              y2="50%"
            >
              <stop offset="5%" stopColor="#9DD9D5"></stop>
              <stop offset="95%" stopColor="#C5E8E6"></stop>
            </linearGradient>
          </defs>
          <path
            d="M0,256L48,240C96,224,192,192,288,181.3C384,171,480,181,576,197.3C672,213,768,235,864,234.7C960,235,1056,213,1152,197.3C1248,181,1344,171,1392,165.3L1440,160L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
            fill="url(#faqWaveGradient3)"
            fillOpacity="1"
          />
        </svg>
      </div>

      {/* FAQ Section */}
      <section className="relative py-20 px-20 bg-[#C5E8E6]">
        {/* Background Paw Prints */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.03]">
          <PawPrint
            size={55}
            className="absolute top-10 left-[8%] rotate-[20deg]"
          />
          <PawPrint
            size={60}
            className="absolute top-40 right-[12%] rotate-[-25deg]"
          />
          <PawPrint
            size={45}
            className="absolute bottom-20 left-[15%] rotate-[30deg]"
          />
          <PawPrint
            size={50}
            className="absolute bottom-10 right-[10%] rotate-[-20deg]"
          />
        </div>

        <div className="relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-[48px] font-nunito font-black text-[#1D3533] leading-tight mb-4">
              Frequently Asked <span className="text-[#3DA99F]">Questions</span>
            </h2>
            <p className="text-[18px] text-[#5C6F6C] leading-relaxed font-medium max-w-2xl mx-auto">
              Everything you need to know about PawPoint and how it can help
              your clinic.
            </p>
          </div>
          <FAQAccordion />
        </div>
      </section>

      {/* Wave Transition from FAQ to CTA */}
      <div className="relative bg-[#C5E8E6]">
        {/* Paw prints over waves */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.04] z-10">
          <PawPrint
            size={32}
            className="absolute top-6 left-[20%] rotate-[18deg]"
          />
          <PawPrint
            size={28}
            className="absolute top-10 right-[30%] rotate-[-22deg]"
          />
          <PawPrint
            size={30}
            className="absolute bottom-8 left-[50%] rotate-[28deg]"
          />
        </div>
        <svg
          width="100%"
          height="120"
          viewBox="0 0 1440 320"
          xmlns="http://www.w3.org/2000/svg"
          className="transition duration-300 ease-in-out delay-150"
          preserveAspectRatio="none"
        >
          <defs>
            <linearGradient
              id="faqToCtaGradient1"
              x1="0%"
              y1="50%"
              x2="100%"
              y2="50%"
            >
              <stop offset="5%" stopColor="#C5E8E6"></stop>
              <stop offset="95%" stopColor="#E8F5F4"></stop>
            </linearGradient>
          </defs>
          <path
            d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,112C672,96,768,96,864,112C960,128,1056,160,1152,165.3C1248,171,1344,149,1392,138.7L1440,128L1440,0L1392,0C1344,0,1248,0,1152,0C1056,0,960,0,864,0C768,0,672,0,576,0C480,0,384,0,288,0C192,0,96,0,48,0L0,0Z"
            fill="url(#faqToCtaGradient1)"
            fillOpacity="0.4"
            transform="scale(1,-1) translate(0,-320)"
          />
          <defs>
            <linearGradient
              id="faqToCtaGradient2"
              x1="0%"
              y1="50%"
              x2="100%"
              y2="50%"
            >
              <stop offset="5%" stopColor="#D4EDE6"></stop>
              <stop offset="95%" stopColor="#F0F9F7"></stop>
            </linearGradient>
          </defs>
          <path
            d="M0,64L48,74.7C96,85,192,107,288,122.7C384,139,480,149,576,138.7C672,128,768,96,864,85.3C960,75,1056,85,1152,101.3C1248,117,1344,139,1392,149.3L1440,160L1440,0L1392,0C1344,0,1248,0,1152,0C1056,0,960,0,864,0C768,0,672,0,576,0C480,0,384,0,288,0C192,0,96,0,48,0L0,0Z"
            fill="url(#faqToCtaGradient2)"
            fillOpacity="0.6"
            transform="scale(1,-1) translate(0,-320)"
          />
          <defs>
            <linearGradient
              id="faqToCtaGradient3"
              x1="0%"
              y1="50%"
              x2="100%"
              y2="50%"
            >
              <stop offset="5%" stopColor="#E8F5F4"></stop>
              <stop offset="95%" stopColor="#FFFFFF"></stop>
            </linearGradient>
          </defs>
          <path
            d="M0,192L48,186.7C96,181,192,171,288,176C384,181,480,203,576,208C672,213,768,203,864,181.3C960,160,1056,128,1152,122.7C1248,117,1344,139,1392,149.3L1440,160L1440,0L1392,0C1344,0,1248,0,1152,0C1056,0,960,0,864,0C768,0,672,0,576,0C480,0,384,0,288,0C192,0,96,0,48,0L0,0Z"
            fill="url(#faqToCtaGradient3)"
            fillOpacity="1"
            transform="scale(1,-1) translate(0,-320)"
          />
        </svg>
      </div>

      {/* CTA Section */}
      <section id="demo" className="relative">
        {/* Top Wave Layers */}
        <div className="relative">
          {/* Paw prints over waves */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.04] z-10">
            <PawPrint
              size={32}
              className="absolute top-6 left-[18%] rotate-[22deg]"
            />
            <PawPrint
              size={28}
              className="absolute top-8 right-[28%] rotate-[-18deg]"
            />
            <PawPrint
              size={35}
              className="absolute bottom-4 left-[45%] rotate-[28deg]"
            />
          </div>
          <svg
            width="100%"
            height="100"
            viewBox="0 0 1440 690"
            xmlns="http://www.w3.org/2000/svg"
            className="transition duration-300 ease-in-out delay-150"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient
                id="ctaTopGradient1"
                x1="0%"
                y1="50%"
                x2="100%"
                y2="50%"
              >
                <stop offset="5%" stopColor="#2A9D8F"></stop>
                <stop offset="95%" stopColor="#7ECDC8"></stop>
              </linearGradient>
            </defs>
            <path
              d="M 0,700 L 0,356 C 67.66923076923078,398.87051282051283 135.33846153846156,441.74102564102566 217,413 C 298.66153846153844,384.25897435897434 394.3153846153846,283.90641025641025 485,231 C 575.6846153846154,178.09358974358975 661.4000000000001,172.63333333333333 743,178 C 824.5999999999999,183.36666666666667 902.0846153846153,199.56025641025641 978,183 C 1053.9153846153847,166.43974358974359 1128.2615384615385,117.12564102564102 1205,78 C 1281.7384615384615,38.87435897435898 1360.8692307692309,9.937179487179488 1440,-19 L 1440,700 L 0,700 Z"
              stroke="none"
              strokeWidth="0"
              fill="url(#ctaTopGradient1)"
              fillOpacity="0.3"
              className="transition-all duration-300 ease-in-out delay-150"
            ></path>
            <defs>
              <linearGradient
                id="ctaTopGradient2"
                x1="0%"
                y1="50%"
                x2="100%"
                y2="50%"
              >
                <stop offset="5%" stopColor="#2A9D8F"></stop>
                <stop offset="95%" stopColor="#7ECDC8"></stop>
              </linearGradient>
            </defs>
            <path
              d="M 0,700 L 0,531 C 53.17435897435897,508.86282051282046 106.34871794871793,486.725641025641 197,497 C 287.65128205128207,507.274358974359 415.7794871794872,549.9602564102564 499,515 C 582.2205128205128,480.0397435897436 620.5333333333334,367.43333333333334 692,325 C 763.4666666666666,282.56666666666666 868.0871794871794,310.30641025641023 964,306 C 1059.9128205128206,301.69358974358977 1147.1179487179488,265.3410256410256 1225,235 C 1302.8820512820512,204.65897435897438 1371.4410256410256,180.3294871794872 1440,156 L 1440,700 L 0,700 Z"
              stroke="none"
              strokeWidth="0"
              fill="url(#ctaTopGradient2)"
              fillOpacity="0.45"
              className="transition-all duration-300 ease-in-out delay-150"
            ></path>
            <defs>
              <linearGradient
                id="ctaTopGradient3"
                x1="0%"
                y1="50%"
                x2="100%"
                y2="50%"
              >
                <stop offset="5%" stopColor="#3DA99F"></stop>
                <stop offset="95%" stopColor="#8DD4CF"></stop>
              </linearGradient>
            </defs>
            <path
              d="M 0,700 L 0,531 C 53.17435897435897,508.86282051282046 106.34871794871793,486.725641025641 197,497 C 287.65128205128207,507.274358974359 415.7794871794872,549.9602564102564 499,515 C 582.2205128205128,480.0397435897436 620.5333333333334,367.43333333333334 692,325 C 763.4666666666666,282.56666666666666 868.0871794871794,310.30641025641023 964,306 C 1059.9128205128206,301.69358974358977 1147.1179487179488,265.3410256410256 1225,235 C 1302.8820512820512,204.65897435897438 1371.4410256410256,180.3294871794872 1440,156 L 1440,700 L 0,700 Z"
              stroke="none"
              strokeWidth="0"
              fill="url(#ctaTopGradient3)"
              fillOpacity="0.6"
              className="transition-all duration-300 ease-in-out delay-150"
            ></path>
            <defs>
              <linearGradient
                id="ctaTopGradient4"
                x1="0%"
                y1="50%"
                x2="100%"
                y2="50%"
              >
                <stop offset="5%" stopColor="#3EB5B0"></stop>
                <stop offset="95%" stopColor="#9DD9D5"></stop>
              </linearGradient>
            </defs>
            <path
              d="M 0,700 L 0,706 C 67.15128205128207,715.6628205128204 134.30256410256413,725.325641025641 221,697 C 307.69743589743587,668.674358974359 413.9410256410257,602.3602564102564 487,578 C 560.0589743589743,553.6397435897436 599.9333333333333,571.2333333333333 676,563 C 752.0666666666667,554.7666666666667 864.3256410256411,520.7064102564103 947,491 C 1029.674358974359,461.2935897435897 1082.7641025641026,435.94102564102565 1160,410 C 1237.2358974358974,384.05897435897435 1338.6179487179488,357.5294871794872 1440,331 L 1440,700 L 0,700 Z"
              stroke="none"
              strokeWidth="0"
              fill="url(#ctaTopGradient4)"
              fillOpacity="1"
              className="transition-all duration-300 ease-in-out delay-150"
            ></path>
          </svg>
        </div>

        {/* CTA Content */}
        <div className="bg-[#3DA99F] relative overflow-hidden">
          {/* Decorative Elements */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.06]">
            <PawPrint
              size={60}
              className="absolute top-10 left-20 rotate-[20deg]"
            />
            <PawPrint
              size={70}
              className="absolute bottom-10 right-20 rotate-[25deg]"
            />
            <PawPrint
              size={45}
              className="absolute top-20 right-[40%] rotate-[-30deg]"
            />
            <PawPrint
              size={50}
              className="absolute bottom-20 left-[35%] rotate-[15deg]"
            />
          </div>

          <div className="px-20 py-14 flex flex-col items-center gap-6 relative z-10">
            <h2 className="text-[52px] font-nunito font-black text-white text-center leading-tight">
              Ready to Never Miss a Call?
            </h2>
            <p className="text-[20px] text-white/90 text-center max-w-2xl font-medium">
              See how PawPoint helps clinics capture more appointments with less
              effort.
            </p>
            <div className="flex gap-6 mt-4">
              <Link
                href="/signup"
                className="px-10 py-5 text-[18px] font-black text-white bg-[#F4A261] rounded-xl hover:bg-[#E78B45] transition-all shadow-[0_8px_25px_rgba(244,162,97,0.4)] hover:shadow-[0_12px_30px_rgba(244,162,97,0.5)]"
              >
                Test the AI
              </Link>
              <Link
                href="/demo"
                className="px-10 py-5 text-[18px] font-black text-[#1D3533] bg-white rounded-xl hover:bg-gray-50 transition-all shadow-lg"
              >
                View Live Demo
              </Link>
            </div>
          </div>
        </div>

        {/* Bottom Wave Layers */}
        <div className="relative bg-[#3EB5B0]">
          {/* Paw prints over waves */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.04] z-10">
            <PawPrint
              size={30}
              className="absolute top-4 left-[22%] rotate-[25deg]"
            />
            <PawPrint
              size={35}
              className="absolute top-8 right-[35%] rotate-[-22deg]"
            />
            <PawPrint
              size={28}
              className="absolute bottom-6 left-[60%] rotate-[32deg]"
            />
          </div>
          <svg
            width="100%"
            height="100"
            viewBox="0 0 1440 690"
            xmlns="http://www.w3.org/2000/svg"
            className="transition duration-300 ease-in-out delay-150"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient
                id="ctaBottomGradient1"
                x1="0%"
                y1="50%"
                x2="100%"
                y2="50%"
              >
                <stop offset="5%" stopColor="#3EB5B0"></stop>
                <stop offset="95%" stopColor="#8DD4CF"></stop>
              </linearGradient>
            </defs>
            <path
              d="M 0,700 L 0,531 C 53.17435897435897,508.86282051282046 106.34871794871793,486.725641025641 197,497 C 287.65128205128207,507.274358974359 415.7794871794872,549.9602564102564 499,515 C 582.2205128205128,480.0397435897436 620.5333333333334,367.43333333333334 692,325 C 763.4666666666666,282.56666666666666 868.0871794871794,310.30641025641023 964,306 C 1059.9128205128206,301.69358974358977 1147.1179487179488,265.3410256410256 1225,235 C 1302.8820512820512,204.65897435897438 1371.4410256410256,180.3294871794872 1440,156 L 1440,700 L 0,700 Z"
              stroke="none"
              strokeWidth="0"
              fill="url(#ctaBottomGradient1)"
              fillOpacity="0.5"
              className="transition-all duration-300 ease-in-out delay-150"
            ></path>
            <defs>
              <linearGradient
                id="ctaBottomGradient2"
                x1="0%"
                y1="50%"
                x2="100%"
                y2="50%"
              >
                <stop offset="5%" stopColor="#5AC4C0"></stop>
                <stop offset="95%" stopColor="#9DD9D5"></stop>
              </linearGradient>
            </defs>
            <path
              d="M 0,700 L 0,706 C 67.15128205128207,715.6628205128204 134.30256410256413,725.325641025641 221,697 C 307.69743589743587,668.674358974359 413.9410256410257,602.3602564102564 487,578 C 560.0589743589743,553.6397435897436 599.9333333333333,571.2333333333333 676,563 C 752.0666666666667,554.7666666666667 864.3256410256411,520.7064102564103 947,491 C 1029.674358974359,461.2935897435897 1082.7641025641026,435.94102564102565 1160,410 C 1237.2358974358974,384.05897435897435 1338.6179487179488,357.5294871794872 1440,331 L 1440,700 L 0,700 Z"
              stroke="none"
              strokeWidth="0"
              fill="url(#ctaBottomGradient2)"
              fillOpacity="0.7"
              className="transition-all duration-300 ease-in-out delay-150"
            ></path>
            <defs>
              <linearGradient
                id="ctaBottomGradient3"
                x1="0%"
                y1="50%"
                x2="100%"
                y2="50%"
              >
                <stop offset="5%" stopColor="#7ECDC8"></stop>
                <stop offset="95%" stopColor="#C5E8E6"></stop>
              </linearGradient>
            </defs>
            <path
              d="M 0,700 L 0,356 C 67.66923076923078,398.87051282051283 135.33846153846156,441.74102564102566 217,413 C 298.66153846153844,384.25897435897434 394.3153846153846,283.90641025641025 485,231 C 575.6846153846154,178.09358974358975 661.4000000000001,172.63333333333333 743,178 C 824.5999999999999,183.36666666666667 902.0846153846153,199.56025641025641 978,183 C 1053.9153846153847,166.43974358974359 1128.2615384615385,117.12564102564102 1205,78 C 1281.7384615384615,38.87435897435898 1360.8692307692309,9.937179487179488 1440,-19 L 1440,700 L 0,700 Z"
              stroke="none"
              strokeWidth="0"
              fill="url(#ctaBottomGradient3)"
              fillOpacity="1"
              className="transition-all duration-300 ease-in-out delay-150"
            ></path>
          </svg>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-100">
        <div className="px-20 py-16">
          <div className="flex flex-col md:flex-row justify-between items-start gap-12">
            {/* Logo and tagline */}
            <div className="flex flex-col items-start gap-6 max-w-[300px]">
              <PawLogo
                height={150}
                paddingTop="0px"
                cropTop={42}
                cropBottom={62}
                cropLeft={32}
              />
              <p className="text-[15px] text-[#5C6F6C] font-medium leading-relaxed">
                The #1 AI Receptionist tool built exclusively for veterinary
                practices.
              </p>
              {/* Social Icons */}
              <div className="flex gap-4 mt-2">
                <Link
                  href="#"
                  className="p-2 bg-gray-50 rounded-full text-[#2D3748] hover:text-[#2A9D8F] transition-all hover:scale-110"
                >
                  <svg
                    className="w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
                  </svg>
                </Link>
                <Link
                  href="#"
                  className="p-2 bg-gray-50 rounded-full text-[#2D3748] hover:text-[#2A9D8F] transition-all hover:scale-110"
                >
                  <svg
                    className="w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                  </svg>
                </Link>
                <Link
                  href="#"
                  className="p-2 bg-gray-50 rounded-full text-[#2D3748] hover:text-[#2A9D8F] transition-all hover:scale-110"
                >
                  <svg
                    className="w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                  </svg>
                </Link>
                <Link
                  href="#"
                  className="p-2 bg-gray-50 rounded-full text-[#2D3748] hover:text-[#2A9D8F] transition-all hover:scale-110"
                >
                  <svg
                    className="w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z" />
                  </svg>
                </Link>
              </div>
            </div>

            {/* Links */}
            <div className="flex flex-wrap gap-16 md:gap-24">
              <div className="flex flex-col gap-5">
                <h4 className="font-nunito font-bold text-[#1D3533] text-[16px] uppercase tracking-wider">
                  Product
                </h4>
                <div className="flex flex-col gap-3">
                  <Link
                    href="/"
                    className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors"
                  >
                    Home
                  </Link>
                  <Link
                    href="#features"
                    className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors"
                  >
                    Features
                  </Link>
                  <Link
                    href="#pricing"
                    className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors"
                  >
                    Pricing
                  </Link>
                  <Link
                    href="#demo"
                    className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors"
                  >
                    Request a Demo
                  </Link>
                </div>
              </div>

              <div className="flex flex-col gap-5">
                <h4 className="font-nunito font-bold text-[#1D3533] text-[16px] uppercase tracking-wider">
                  Why PawPoint
                </h4>
                <div className="flex flex-col gap-3">
                  <Link
                    href="/about"
                    className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors"
                  >
                    About Us
                  </Link>
                  <Link
                    href="/faq"
                    className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors"
                  >
                    FAQ
                  </Link>
                  <Link
                    href="#"
                    className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors"
                  >
                    Contact
                  </Link>
                </div>
              </div>

              <div className="flex flex-col gap-5">
                <h4 className="font-nunito font-bold text-[#1D3533] text-[16px] uppercase tracking-wider">
                  Company
                </h4>
                <div className="flex flex-col gap-3">
                  <Link
                    href="#"
                    className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors"
                  >
                    Terms of Service
                  </Link>
                  <Link
                    href="#"
                    className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors"
                  >
                    Privacy Policy
                  </Link>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-16 pt-8 border-t border-gray-50 flex justify-between items-center text-[14px] text-gray-400 font-medium">
            <p>© 2026 PawPoint AI. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Contact Form Modal */}
      {showContactForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100] p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-zinc-200 bg-gradient-to-r from-teal-50 to-teal-100/50">
              <div>
                <h2 className="text-xl font-bold text-zinc-900">
                  Request a Demo
                </h2>
                <p className="text-sm text-zinc-600">
                  We&apos;ll get back to you within 24 hours
                </p>
              </div>
              <button
                onClick={() => setShowContactForm(false)}
                className="p-2 hover:bg-white/60 rounded-xl transition-colors"
              >
                <X className="w-5 h-5 text-zinc-600" />
              </button>
            </div>

            {/* Form Content */}
            <div className="p-6">
              {formSubmitted ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg
                      className="w-8 h-8 text-teal-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-zinc-900 mb-2">
                    Thank you!
                  </h3>
                  <p className="text-zinc-600">We&apos;ll be in touch soon.</p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-zinc-700 mb-1">
                      Your Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.name}
                      onChange={(e) =>
                        setFormData({ ...formData, name: e.target.value })
                      }
                      className="w-full px-4 py-3 border border-zinc-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-all"
                      placeholder="John Doe"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-zinc-700 mb-1">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      required
                      value={formData.email}
                      onChange={(e) =>
                        setFormData({ ...formData, email: e.target.value })
                      }
                      className="w-full px-4 py-3 border border-zinc-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-all"
                      placeholder="john@clinic.com"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-zinc-700 mb-1">
                      Clinic Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.clinicName}
                      onChange={(e) =>
                        setFormData({ ...formData, clinicName: e.target.value })
                      }
                      className="w-full px-4 py-3 border border-zinc-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-all"
                      placeholder="PawPoint Animal Hospital"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-zinc-700 mb-1">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) =>
                        setFormData({ ...formData, phone: e.target.value })
                      }
                      className="w-full px-4 py-3 border border-zinc-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-all"
                      placeholder="+1 (555) 123-4567"
                    />
                  </div>

                  <button
                    type="submit"
                    className="w-full py-3 bg-[#3DA99F] hover:bg-[#2A9D8F] text-white font-bold rounded-xl transition-colors shadow-[0_4px_14px_0_rgba(61,169,159,0.3)]"
                  >
                    Submit Request
                  </button>
                </form>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
