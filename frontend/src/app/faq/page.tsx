import Link from "next/link";
import { Logo, NAVBAR_HEIGHT } from "@/components/Logo";
import { PawPrint } from "@/components/PawPrint";
import { faqData } from "@/data/faqData";

const PawLogo = Logo;

export default function FAQPage() {
  return (
    <div className="flex min-h-screen flex-col bg-white overflow-x-hidden">
      {/* Header */}
      <header
        className="flex items-center justify-between px-20 bg-white relative z-20 border-b border-white shadow-sm"
        style={{ height: `${NAVBAR_HEIGHT}px` }}
      >
        <div className="flex items-center gap-2">
          <PawLogo />
        </div>
        <nav className="flex items-center gap-10">
          <Link
            href="/#features"
            className="text-[17px] font-medium text-[#4A5568] hover:text-[#2A9D8F] transition-colors"
          >
            Features
          </Link>
          <Link
            href="/faq"
            className="text-[17px] font-medium text-[#3DA99F] transition-colors"
          >
            FAQ
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
            className="text-[17px] font-medium text-[#4A5568] hover:text-[#2A9D8F] transition-colors"
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
      <section className="relative pt-16 pb-12 overflow-visible bg-gradient-to-b from-[#7ECDC8]/10 to-white">
        {/* Background Paw Prints */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.03]">
          <PawPrint
            size={60}
            className="absolute top-10 left-10 rotate-[15deg]"
          />
          <PawPrint
            size={70}
            className="absolute top-40 right-20 rotate-[-25deg]"
          />
          <PawPrint
            size={45}
            className="absolute top-20 left-[20%] rotate-[45deg]"
          />
          <PawPrint
            size={55}
            className="absolute bottom-10 right-[15%] rotate-[-35deg]"
          />
        </div>

        <div className="relative z-10 px-20">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-[56px] font-nunito font-black text-[#1D3533] leading-[1.1] tracking-tight mb-6">
              Frequently Asked <span className="text-[#3DA99F]">Questions</span>
            </h1>
            <p className="text-[20px] text-[#5C6F6C] leading-relaxed font-medium">
              Everything you need to know about PawPoint and how it can help
              your clinic.
            </p>
          </div>
        </div>
      </section>

      {/* FAQ Content */}
      <section className="relative py-16 px-20 bg-white">
        <div className="max-w-4xl mx-auto">
          <div className="space-y-6">
            {faqData.map((faq, index) => (
              <div
                key={index}
                className="bg-white rounded-2xl border-2 border-gray-100 p-8 hover:border-[#3DA99F]/30 hover:shadow-lg transition-all duration-300"
              >
                <h3 className="text-[20px] font-nunito font-bold text-[#1D3533] mb-4 flex items-start gap-3">
                  <span className="text-[#3DA99F] text-[24px] font-black flex-shrink-0">
                    {index + 1}.
                  </span>
                  <span>{faq.question}</span>
                </h3>
                <p className="text-[16px] text-[#5C6F6C] leading-relaxed font-medium pl-10">
                  {faq.answer}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-20 bg-gradient-to-b from-white to-[#7ECDC8]/10">
        {/* Background Paw Prints */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.03]">
          <PawPrint
            size={50}
            className="absolute top-10 left-[10%] rotate-[20deg]"
          />
          <PawPrint
            size={60}
            className="absolute bottom-10 right-[10%] rotate-[-20deg]"
          />
        </div>

        <div className="relative z-10 px-20">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-[42px] font-nunito font-black text-[#1D3533] leading-tight mb-6">
              Still have questions?
            </h2>
            <p className="text-[18px] text-[#5C6F6C] leading-relaxed font-medium mb-8">
              Our team is here to help. Schedule a demo to see PawPoint in
              action and get answers to all your questions.
            </p>
            <div className="flex gap-4 justify-center">
              <Link
                href="/signup"
                className="px-10 py-4 text-[18px] font-bold text-white bg-[#3DA99F] rounded-xl hover:bg-[#2A9D8F] transition-all shadow-[0_6px_20px_rgba(61,169,159,0.4)]"
              >
                Schedule a Demo
              </Link>
              <Link
                href="/about"
                className="px-10 py-4 text-[18px] font-bold text-[#2D3748] bg-white rounded-xl border-2 border-[#E2E8F0] hover:bg-gray-50 transition-all"
              >
                Learn More
              </Link>
            </div>
          </div>
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
                    href="/#demo"
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
    </div>
  );
}
