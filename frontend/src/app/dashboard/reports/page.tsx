/**
 * Reports page - placeholder for future implementation.
 */

export default function ReportsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-[#1D3533]">Reports</h1>
        <p className="text-[#1D3533]/60 mt-2">
          Generate and view clinic reports and analytics.
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
                d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-[#1D3533] mb-2">
            Coming Soon
          </h2>
          <p className="text-[#1D3533]/60">
            The reports feature is under development and will be available soon.
          </p>
        </div>
      </div>
    </div>
  );
}
