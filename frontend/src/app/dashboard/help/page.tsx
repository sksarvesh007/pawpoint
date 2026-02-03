/**
 * Help page - placeholder for future implementation.
 */

export default function HelpPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-[#1D3533]">Help</h1>
        <p className="text-[#1D3533]/60 mt-2">
          Get help and support for using PawPoint.
        </p>
      </div>

      <div className="bg-white/60 backdrop-blur-sm rounded-2xl border border-white/80 shadow-sm p-12 text-center">
        <div className="max-w-md mx-auto">
          <div className="w-16 h-16 bg-gradient-to-br from-[#3EB5B0] to-[#2A8A86] rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-[#1D3533] mb-2">
            Coming Soon
          </h2>
          <p className="text-[#1D3533]/60">
            The help center is under development and will be available soon.
          </p>
        </div>
      </div>
    </div>
  );
}
