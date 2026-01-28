import Link from "next/link";
import Image from "next/image";
import { Logo, NAVBAR_HEIGHT } from "@/components/Logo";
import { PawBackground } from "@/components/PawBackground";
import { PawPrint } from "@/components/PawPrint";

const PawLogo = Logo;

export default function AboutPage() {
  return (
    <div className="flex min-h-screen flex-col bg-white overflow-x-hidden">
      {/* Header */}
      <header
        className="flex items-center justify-between px-20 bg-white relative z-20 border-b border-white shadow-sm"
        style={{ height: `${NAVBAR_HEIGHT}px` }}
      >
        <div className="flex items-center gap-2">
          <Link href="/">
            <PawLogo />
          </Link>
        </div>
        <nav className="flex items-center gap-10">
          <Link
            href="/#features"
            className="text-[17px] font-medium text-[#4A5568] hover:text-[#2A9D8F] transition-colors"
          >
            Features
          </Link>
          <Link
            href="/#pricing"
            className="text-[17px] font-medium text-[#4A5568] hover:text-[#2A9D8F] transition-colors"
          >
            Pricing
          </Link>
          <Link
            href="/#demo"
            className="text-[17px] font-medium text-[#4A5568] hover:text-[#2A9D8F] transition-colors"
          >
            Demo
          </Link>
          <Link
            href="/about"
            className="text-[17px] font-medium text-[#2A9D8F] transition-colors"
          >
            About Us
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
      <section className="relative pt-12 pb-32 overflow-visible">
        {/* Top Wave Background */}
        <div className="absolute top-0 left-0 right-0 h-[300px] pointer-events-none overflow-hidden">
          <svg
            width="100%"
            height="300"
            viewBox="0 0 1440 690"
            xmlns="http://www.w3.org/2000/svg"
            className="absolute top-0 transition duration-300 ease-in-out delay-150"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient
                id="topBgGradient1"
                x1="0%"
                y1="50%"
                x2="100%"
                y2="50%"
              >
                <stop offset="5%" stopColor="#C5E8E6"></stop>
                <stop offset="95%" stopColor="#E8F7F6"></stop>
              </linearGradient>
            </defs>
            <path
              d="M 0,700 L 0,356 C 67.66923076923078,398.87051282051283 135.33846153846156,441.74102564102566 217,413 C 298.66153846153844,384.25897435897434 394.3153846153846,283.90641025641025 485,231 C 575.6846153846154,178.09358974358975 661.4000000000001,172.63333333333333 743,178 C 824.5999999999999,183.36666666666667 902.0846153846153,199.56025641025641 978,183 C 1053.9153846153847,166.43974358974359 1128.2615384615385,117.12564102564102 1205,78 C 1281.7384615384615,38.87435897435898 1360.8692307692309,9.937179487179488 1440,-19 L 1440,0 L 0,0 Z"
              stroke="none"
              strokeWidth="0"
              fill="url(#topBgGradient1)"
              fillOpacity="0.25"
              className="transition-all duration-300 ease-in-out delay-150"
            ></path>
            <defs>
              <linearGradient
                id="topBgGradient2"
                x1="0%"
                y1="50%"
                x2="100%"
                y2="50%"
              >
                <stop offset="5%" stopColor="#D0F0EE"></stop>
                <stop offset="95%" stopColor="#F0F9F8"></stop>
              </linearGradient>
            </defs>
            <path
              d="M 0,700 L 0,531 C 53.17435897435897,508.86282051282046 106.34871794871793,486.725641025641 197,497 C 287.65128205128207,507.274358974359 415.7794871794872,549.9602564102564 499,515 C 582.2205128205128,480.0397435897436 620.5333333333334,367.43333333333334 692,325 C 763.4666666666666,282.56666666666666 868.0871794871794,310.30641025641023 964,306 C 1059.9128205128206,301.69358974358977 1147.1179487179488,265.3410256410256 1225,235 C 1302.8820512820512,204.65897435897438 1371.4410256410256,180.3294871794872 1440,156 L 1440,0 L 0,0 Z"
              stroke="none"
              strokeWidth="0"
              fill="url(#topBgGradient2)"
              fillOpacity="0.2"
              className="transition-all duration-300 ease-in-out delay-150"
            ></path>
          </svg>
        </div>

        {/* Background Paw Prints */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.03]">
          <PawPrint
            size={40}
            className="absolute top-20 left-10 rotate-[20deg]"
          />
          <PawPrint
            size={50}
            className="absolute top-40 right-20 rotate-[15deg]"
          />
          <PawPrint
            size={30}
            className="absolute top-60 left-[30%] rotate-[-20deg]"
          />
          <PawPrint
            size={35}
            className="absolute bottom-20 right-[40%] rotate-[35deg]"
          />
          <PawPrint
            size={45}
            className="absolute top-80 right-[50%] rotate-[-25deg]"
          />
        </div>

        {/* Hero Content */}
        <div className="relative z-10 flex flex-col md:flex-row items-start justify-between px-20 gap-8">
          <div className="flex flex-col gap-6 max-w-[500px] pt-8">
            <h1 className="text-[42px] font-nunito font-black text-[#1D3533] leading-[1.15] tracking-tight">
              About PawPoint:
              <br />
              <span className="text-[#3DA99F]">Pioneering AI for</span>
              <br />
              <span className="text-[#3DA99F]">Veterinary Care</span>
            </h1>
            <p className="text-[16px] text-[#5C6F6C] leading-relaxed font-medium">
              At PawPoint, we&apos;re transforming how veterinary clinics
              connect with pet owners—making sure pets get the care they need,
              when they need it, while also giving veterinary teams more time to
              provide personalized, compassionate care.
            </p>
            <div className="flex gap-4 mt-2">
              <Link
                href="/signup"
                className="px-6 py-3 text-[15px] font-bold text-white bg-[#F4A261] rounded-lg hover:bg-[#E78B45] transition-all shadow-[0_4px_14px_rgba(244,162,97,0.3)]"
              >
                Request a Demo
              </Link>
              <Link
                href="#contact"
                className="px-6 py-3 text-[15px] font-bold text-[#2D3748] bg-white rounded-lg border-2 border-[#E2E8F0] hover:bg-gray-50 transition-all"
              >
                Contact Us
              </Link>
            </div>
          </div>

          {/* Dog Doctor Image */}
          <div className="relative flex-shrink-0">
            <Image
              src="/dog_doctor.png"
              alt="Veterinarian with dog and cat"
              width={450}
              height={450}
              className="object-contain"
              priority
            />
          </div>
        </div>

        {/* Wave Divider */}
        <div className="absolute bottom-0 left-0 right-0 w-full">
          {/* Paw prints over waves */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.04] z-10">
            <PawPrint
              size={35}
              className="absolute top-20 left-[12%] rotate-[22deg]"
            />
            <PawPrint
              size={40}
              className="absolute top-40 right-[18%] rotate-[-28deg]"
            />
            <PawPrint
              size={28}
              className="absolute bottom-20 left-[35%] rotate-[18deg]"
            />
            <PawPrint
              size={32}
              className="absolute top-32 right-[55%] rotate-[-32deg]"
            />
            <PawPrint
              size={36}
              className="absolute bottom-10 right-[8%] rotate-[35deg]"
            />
            <PawPrint
              size={30}
              className="absolute top-50 left-[70%] rotate-[-15deg]"
            />
          </div>
          <svg
            width="100%"
            height="300"
            viewBox="0 0 1440 690"
            xmlns="http://www.w3.org/2000/svg"
            className="transition duration-300 ease-in-out delay-150"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient
                id="gradient1"
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
              fill="url(#gradient1)"
              fillOpacity="0.4"
              className="transition-all duration-300 ease-in-out delay-150 path-0"
            ></path>
            <defs>
              <linearGradient
                id="gradient2"
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
              fill="url(#gradient2)"
              fillOpacity="0.53"
              className="transition-all duration-300 ease-in-out delay-150 path-1"
            ></path>
            <defs>
              <linearGradient
                id="gradient3"
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
              d="M 0,700 L 0,706 C 67.15128205128207,715.6628205128204 134.30256410256413,725.325641025641 221,697 C 307.69743589743587,668.674358974359 413.9410256410257,602.3602564102564 487,578 C 560.0589743589743,553.6397435897436 599.9333333333333,571.2333333333333 676,563 C 752.0666666666667,554.7666666666667 864.3256410256411,520.7064102564103 947,491 C 1029.674358974359,461.2935897435897 1082.7641025641026,435.94102564102565 1160,410 C 1237.2358974358974,384.05897435897435 1338.6179487179488,357.5294871794872 1440,331 L 1440,700 L 0,700 Z"
              stroke="none"
              strokeWidth="0"
              fill="url(#gradient3)"
              fillOpacity="1"
              className="transition-all duration-300 ease-in-out delay-150 path-2"
            ></path>
          </svg>
        </div>
      </section>

      {/* What We Do & Our Mission Section */}
      <section className="relative bg-white py-16 px-20">
        {/* Background Paw Prints */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.03]">
          <PawPrint
            size={55}
            className="absolute top-10 right-20 rotate-[-15deg]"
          />
          <PawPrint
            size={50}
            className="absolute bottom-20 left-10 rotate-[25deg]"
          />
          <PawPrint
            size={40}
            className="absolute top-32 left-[45%] rotate-[40deg]"
          />
        </div>

        <div className="relative z-10 flex flex-col md:flex-row gap-12 items-start justify-between max-w-7xl mx-auto">
          {/* What We Do */}
          <div className="flex-1 max-w-[300px]">
            <h2 className="text-[26px] font-nunito font-black text-[#1D3533] mb-4">
              What We Do
            </h2>
            <p className="text-[14px] text-[#5C6F6C] leading-relaxed font-medium mb-4">
              PawPoint is an innovative AI-powered virtual receptionist service
              designed specifically for veterinary clinics.
            </p>
            <p className="text-[14px] text-[#5C6F6C] leading-relaxed font-medium">
              Our system answers calls 24/7, schedules appointments, and ensures
              no pet care requests are missed.
            </p>
          </div>

          {/* Phone Mockup */}
          <div className="relative flex-shrink-0">
            {/* Paw Background with Circles */}
            <PawBackground
              pawCount={5}
              circleCount={0}
              pawOpacity={0.1}
              circleOpacity={0}
              pawSizeRange={[35, 60]}
              circleSizeRange={[0, 0]}
              className="w-[350px] h-[480px] absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 -z-10"
            />
            {/* iPhone Frame */}
            <div className="relative w-[200px] h-[400px] bg-[#2D3436] rounded-[35px] p-[8px] shadow-[0_25px_60px_rgba(0,0,0,0.15)]">
              {/* Screen Content */}
              <div className="relative w-full h-full bg-[#3DA99F] rounded-[28px] overflow-hidden flex flex-col items-center">
                {/* Dynamic Island */}
                <div className="absolute top-2 left-1/2 -translate-x-1/2 w-[60px] h-[18px] bg-black rounded-full z-20"></div>

                {/* Content Area */}
                <div className="w-full h-full flex flex-col items-center pt-10 px-4 gap-3">
                  {/* Avatar */}
                  <div className="w-14 h-14 bg-[#F4A261] rounded-full flex items-center justify-center shadow-lg ring-2 ring-white/20 mt-2">
                    <svg
                      width="28"
                      height="28"
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
                    <h3 className="text-[16px] font-nunito font-bold text-white tracking-tight">
                      PawPoint AI
                    </h3>
                    <p className="text-[11px] text-white/80 font-medium">
                      answering...
                    </p>
                  </div>

                  {/* Message Bubble */}
                  <div className="bg-white rounded-[16px] px-4 py-3 w-full shadow-md">
                    <p className="text-[11px] text-[#2D3748] leading-relaxed font-medium">
                      Hi Thanks for calling.
                      <br />
                      How can we assist you and your pet today?
                    </p>
                  </div>

                  {/* Appointment Box */}
                  <div className="bg-white rounded-[14px] px-4 py-3 w-full shadow-md flex items-center justify-between">
                    <span className="text-[10px] font-bold text-[#2D3748] leading-tight">
                      Appointment Request
                      <br />
                      Captured
                    </span>
                    <div className="w-5 h-5 rounded-full bg-[#E0F2F1] flex items-center justify-center ml-2">
                      <span className="text-[#3DA99F] text-xs font-black">
                        ✓
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Decorative pets around phone */}
            <div className="absolute -left-8 -bottom-2 w-16 h-16">
              <svg viewBox="0 0 64 64" fill="none">
                <circle cx="32" cy="40" r="20" fill="#F4A261" />
                <circle cx="22" cy="28" r="8" fill="#F4A261" />
                <circle cx="42" cy="28" r="8" fill="#F4A261" />
                <circle cx="32" cy="44" r="6" fill="#2D3436" />
                <circle cx="26" cy="38" r="3" fill="#2D3436" />
                <circle cx="38" cy="38" r="3" fill="#2D3436" />
              </svg>
            </div>
            <div className="absolute -right-6 -bottom-2 w-14 h-14">
              <svg viewBox="0 0 56 56" fill="none">
                <ellipse cx="28" cy="36" rx="16" ry="14" fill="#F5A623" />
                <polygon points="18,26 14,12 24,22" fill="#F5A623" />
                <polygon points="38,26 42,12 32,22" fill="#F5A623" />
                <circle cx="22" cy="32" r="2" fill="#2D3436" />
                <circle cx="34" cy="32" r="2" fill="#2D3436" />
                <ellipse cx="28" cy="36" rx="3" ry="2" fill="#FF8C94" />
              </svg>
            </div>
          </div>

          {/* Our Mission */}
          <div className="flex-1 max-w-[380px]">
            <h2 className="text-[26px] font-nunito font-black text-[#1D3533] mb-4">
              Our Mission
            </h2>
            <p className="text-[14px] text-[#5C6F6C] leading-relaxed font-medium">
              At PawPoint, our mission is to enhance the efficiency of
              veterinary clinics by leveraging cutting-edge technology. We
              believe in the power of AI to support and simplify the valuable
              work that veterinarians and their teams do each day. By providing
              tools that automate routine tasks, we empower clinics to improve
              client communication and focus on what matters most — caring for
              pets.
            </p>
          </div>
        </div>
      </section>

      {/* Wave Divider to Why Choose Section */}
      <div className="relative">
        {/* Paw prints over waves */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.04] z-10">
          <PawPrint
            size={32}
            className="absolute top-4 left-[20%] rotate-[18deg]"
          />
          <PawPrint
            size={28}
            className="absolute top-6 right-[30%] rotate-[-25deg]"
          />
          <PawPrint
            size={25}
            className="absolute bottom-2 left-[50%] rotate-[30deg]"
          />
        </div>
        <svg
          width="100%"
          height="60"
          viewBox="0 0 1440 690"
          xmlns="http://www.w3.org/2000/svg"
          className="transition duration-300 ease-in-out delay-150"
          preserveAspectRatio="none"
        >
          <defs>
            <linearGradient
              id="whyChooseGradient1"
              x1="0%"
              y1="50%"
              x2="100%"
              y2="50%"
            >
              <stop offset="5%" stopColor="#C5E8E6"></stop>
              <stop offset="95%" stopColor="#E8F7F6"></stop>
            </linearGradient>
          </defs>
          <path
            d="M 0,700 L 0,356 C 67.66923076923078,398.87051282051283 135.33846153846156,441.74102564102566 217,413 C 298.66153846153844,384.25897435897434 394.3153846153846,283.90641025641025 485,231 C 575.6846153846154,178.09358974358975 661.4000000000001,172.63333333333333 743,178 C 824.5999999999999,183.36666666666667 902.0846153846153,199.56025641025641 978,183 C 1053.9153846153847,166.43974358974359 1128.2615384615385,117.12564102564102 1205,78 C 1281.7384615384615,38.87435897435898 1360.8692307692309,9.937179487179488 1440,-19 L 1440,700 L 0,700 Z"
            stroke="none"
            strokeWidth="0"
            fill="url(#whyChooseGradient1)"
            fillOpacity="0.3"
            className="transition-all duration-300 ease-in-out delay-150"
          ></path>
          <defs>
            <linearGradient
              id="whyChooseGradient2"
              x1="0%"
              y1="50%"
              x2="100%"
              y2="50%"
            >
              <stop offset="5%" stopColor="#8DD4CF"></stop>
              <stop offset="95%" stopColor="#C5E8E6"></stop>
            </linearGradient>
          </defs>
          <path
            d="M 0,700 L 0,531 C 53.17435897435897,508.86282051282046 106.34871794871793,486.725641025641 197,497 C 287.65128205128207,507.274358974359 415.7794871794872,549.9602564102564 499,515 C 582.2205128205128,480.0397435897436 620.5333333333334,367.43333333333334 692,325 C 763.4666666666666,282.56666666666666 868.0871794871794,310.30641025641023 964,306 C 1059.9128205128206,301.69358974358977 1147.1179487179488,265.3410256410256 1225,235 C 1302.8820512820512,204.65897435897438 1371.4410256410256,180.3294871794872 1440,156 L 1440,700 L 0,700 Z"
            stroke="none"
            strokeWidth="0"
            fill="url(#whyChooseGradient2)"
            fillOpacity="0.45"
            className="transition-all duration-300 ease-in-out delay-150"
          ></path>
          <defs>
            <linearGradient
              id="whyChooseGradient3"
              x1="0%"
              y1="50%"
              x2="100%"
              y2="50%"
            >
              <stop offset="5%" stopColor="#7ECDC8"></stop>
              <stop offset="95%" stopColor="#9DD9D5"></stop>
            </linearGradient>
          </defs>
          <path
            d="M 0,700 L 0,531 C 53.17435897435897,508.86282051282046 106.34871794871793,486.725641025641 197,497 C 287.65128205128207,507.274358974359 415.7794871794872,549.9602564102564 499,515 C 582.2205128205128,480.0397435897436 620.5333333333334,367.43333333333334 692,325 C 763.4666666666666,282.56666666666666 868.0871794871794,310.30641025641023 964,306 C 1059.9128205128206,301.69358974358977 1147.1179487179488,265.3410256410256 1225,235 C 1302.8820512820512,204.65897435897438 1371.4410256410256,180.3294871794872 1440,156 L 1440,700 L 0,700 Z"
            stroke="none"
            strokeWidth="0"
            fill="url(#whyChooseGradient3)"
            fillOpacity="0.6"
            className="transition-all duration-300 ease-in-out delay-150"
          ></path>
          <defs>
            <linearGradient
              id="whyChooseGradient4"
              x1="0%"
              y1="50%"
              x2="100%"
              y2="50%"
            >
              <stop offset="5%" stopColor="#D0F0EE"></stop>
              <stop offset="95%" stopColor="#F8F9F7"></stop>
            </linearGradient>
          </defs>
          <path
            d="M 0,700 L 0,706 C 67.15128205128207,715.6628205128204 134.30256410256413,725.325641025641 221,697 C 307.69743589743587,668.674358974359 413.9410256410257,602.3602564102564 487,578 C 560.0589743589743,553.6397435897436 599.9333333333333,571.2333333333333 676,563 C 752.0666666666667,554.7666666666667 864.3256410256411,520.7064102564103 947,491 C 1029.674358974359,461.2935897435897 1082.7641025641026,435.94102564102565 1160,410 C 1237.2358974358974,384.05897435897435 1338.6179487179488,357.5294871794872 1440,331 L 1440,700 L 0,700 Z"
            stroke="none"
            strokeWidth="0"
            fill="url(#whyChooseGradient4)"
            fillOpacity="1"
            className="transition-all duration-300 ease-in-out delay-150"
          ></path>
        </svg>
      </div>

      {/* Why Choose PawPoint Section */}
      <section className="relative bg-[#F8F9F7] py-16 px-20">
        <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.03]">
          <PawPrint
            size={50}
            className="absolute top-10 left-20 rotate-[-20deg]"
          />
          <PawPrint
            size={60}
            className="absolute bottom-10 right-20 rotate-[15deg]"
          />
          <PawPrint
            size={35}
            className="absolute top-[40%] right-[45%] rotate-[30deg]"
          />
        </div>

        <div className="relative z-10 flex flex-col items-center gap-6 max-w-3xl mx-auto text-center">
          <h2 className="text-[36px] font-nunito font-black text-[#1D3533]">
            Why Choose PawPoint?
          </h2>
          <p className="text-[16px] text-[#5C6F6C] font-medium">
            Experience the future of veterinary care scheduling
          </p>
          <div className="flex gap-4 mt-4">
            <Link
              href="/signup"
              className="px-8 py-3 text-[15px] font-bold text-white bg-[#F4A261] rounded-lg hover:bg-[#E78B45] transition-all shadow-[0_4px_14px_rgba(244,162,97,0.3)]"
            >
              Request a Demo
            </Link>
            <Link
              href="#contact"
              className="px-8 py-3 text-[15px] font-bold text-[#2D3748] bg-white rounded-lg border-2 border-[#E2E8F0] hover:bg-gray-50 transition-all"
            >
              Contact Us
            </Link>
          </div>
        </div>
      </section>

      {/* Get Started CTA Section */}
      <section id="contact" className="relative">
        {/* Top Wave Layers */}
        <div className="relative">
          {/* Paw prints over waves */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.04] z-10">
            <PawPrint
              size={30}
              className="absolute top-5 left-[15%] rotate-[20deg]"
            />
            <PawPrint
              size={32}
              className="absolute top-7 right-[25%] rotate-[-25deg]"
            />
            <PawPrint
              size={28}
              className="absolute bottom-3 left-[48%] rotate-[30deg]"
            />
          </div>
          <svg
            width="100%"
            height="80"
            viewBox="0 0 1440 690"
            xmlns="http://www.w3.org/2000/svg"
            className="transition duration-300 ease-in-out delay-150"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient
                id="aboutCtaTopGradient1"
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
              fill="url(#aboutCtaTopGradient1)"
              fillOpacity="0.35"
              className="transition-all duration-300 ease-in-out delay-150"
            ></path>
            <defs>
              <linearGradient
                id="aboutCtaTopGradient2"
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
              fill="url(#aboutCtaTopGradient2)"
              fillOpacity="0.55"
              className="transition-all duration-300 ease-in-out delay-150"
            ></path>
            <defs>
              <linearGradient
                id="aboutCtaTopGradient3"
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
              fill="url(#aboutCtaTopGradient3)"
              fillOpacity="1"
              className="transition-all duration-300 ease-in-out delay-150"
            ></path>
          </svg>
        </div>

        {/* CTA Content */}
        <div className="bg-[#3DA99F] relative overflow-hidden">
          {/* Decorative Elements */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.05]">
            <PawPrint
              size={55}
              className="absolute top-6 left-20 rotate-[18deg]"
            />
            <PawPrint
              size={65}
              className="absolute bottom-6 right-20 rotate-[25deg]"
            />
            <PawPrint
              size={40}
              className="absolute top-12 right-[40%] rotate-[-30deg]"
            />
            <PawPrint
              size={45}
              className="absolute bottom-12 left-[35%] rotate-[35deg]"
            />
          </div>

          <div className="px-20 py-16 flex flex-col items-center gap-6 relative z-10">
            <h2 className="text-[36px] font-nunito font-black text-white text-center leading-tight">
              Get Started with PawPoint
            </h2>
            <p className="text-[16px] text-white/90 text-center max-w-xl font-medium">
              Experience the future of veterinary care scheduling.
            </p>
            <div className="flex gap-4 mt-2">
              <Link
                href="/signup"
                className="px-8 py-3 text-[15px] font-bold text-white bg-[#F4A261] rounded-lg hover:bg-[#E78B45] transition-all shadow-[0_6px_20px_rgba(244,162,97,0.4)]"
              >
                Request a Demo
              </Link>
              <Link
                href="#contact"
                className="px-8 py-3 text-[15px] font-bold text-[#1D3533] bg-white rounded-lg hover:bg-gray-50 transition-all shadow-lg"
              >
                Contact Us
              </Link>
            </div>
          </div>
        </div>

        {/* Bottom Wave Layers */}
        <div className="relative bg-[#3EB5B0]">
          {/* Paw prints over waves */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.04] z-10">
            <PawPrint
              size={28}
              className="absolute top-4 left-[20%] rotate-[22deg]"
            />
            <PawPrint
              size={32}
              className="absolute top-6 right-[32%] rotate-[-28deg]"
            />
            <PawPrint
              size={26}
              className="absolute bottom-5 left-[55%] rotate-[35deg]"
            />
          </div>
          <svg
            width="100%"
            height="80"
            viewBox="0 0 1440 690"
            xmlns="http://www.w3.org/2000/svg"
            className="transition duration-300 ease-in-out delay-150"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient
                id="aboutCtaBottomGradient1"
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
              d="M 0,700 L 0,356 C 67.66923076923078,398.87051282051283 135.33846153846156,441.74102564102566 217,413 C 298.66153846153844,384.25897435897434 394.3153846153846,283.90641025641025 485,231 C 575.6846153846154,178.09358974358975 661.4000000000001,172.63333333333333 743,178 C 824.5999999999999,183.36666666666667 902.0846153846153,199.56025641025641 978,183 C 1053.9153846153847,166.43974358974359 1128.2615384615385,117.12564102564102 1205,78 C 1281.7384615384615,38.87435897435898 1360.8692307692309,9.937179487179488 1440,-19 L 1440,700 L 0,700 Z"
              stroke="none"
              strokeWidth="0"
              fill="url(#aboutCtaBottomGradient1)"
              fillOpacity="0.4"
              className="transition-all duration-300 ease-in-out delay-150"
            ></path>
            <defs>
              <linearGradient
                id="aboutCtaBottomGradient2"
                x1="0%"
                y1="50%"
                x2="100%"
                y2="50%"
              >
                <stop offset="5%" stopColor="#8DD4CF"></stop>
                <stop offset="95%" stopColor="#D0F0EE"></stop>
              </linearGradient>
            </defs>
            <path
              d="M 0,700 L 0,706 C 67.15128205128207,715.6628205128204 134.30256410256413,725.325641025641 221,697 C 307.69743589743587,668.674358974359 413.9410256410257,602.3602564102564 487,578 C 560.0589743589743,553.6397435897436 599.9333333333333,571.2333333333333 676,563 C 752.0666666666667,554.7666666666667 864.3256410256411,520.7064102564103 947,491 C 1029.674358974359,461.2935897435897 1082.7641025641026,435.94102564102565 1160,410 C 1237.2358974358974,384.05897435897435 1338.6179487179488,357.5294871794872 1440,331 L 1440,700 L 0,700 Z"
              stroke="none"
              strokeWidth="0"
              fill="url(#aboutCtaBottomGradient2)"
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
              <div className="flex items-center gap-2">
                <Link href="/">
                  <PawLogo />
                </Link>
              </div>
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
                    href="/#features"
                    className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors"
                  >
                    Features
                  </Link>
                  <Link
                    href="/#pricing"
                    className="text-[15px] font-medium text-[#718096] hover:text-[#2A9D8F] transition-colors"
                  >
                    Pricing
                  </Link>
                  <Link
                    href="/signup"
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
                    href="#"
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
    </div>
  );
}
