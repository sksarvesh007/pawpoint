/**
 * Widgets page - placeholder for future implementation.
 */

export default function WidgetsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-[#1D3533]">Widgets</h1>
        <p className="text-[#1D3533]/60 mt-2">
          Customize your dashboard with widgets.
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
                d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 12a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1v-7z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-[#1D3533] mb-2">
            Coming Soon
          </h2>
          <p className="text-[#1D3533]/60">
            The widgets feature is under development and will be available soon.
          </p>
        </div>
      </div>
    </div>
  );
}
