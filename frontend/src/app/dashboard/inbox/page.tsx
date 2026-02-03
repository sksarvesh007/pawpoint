/**
 * Inbox page - placeholder for future implementation.
 */

export default function InboxPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-[#1D3533]">Inbox</h1>
        <p className="text-[#1D3533]/60 mt-2">
          View and manage your messages and notifications.
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
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-[#1D3533] mb-2">
            Coming Soon
          </h2>
          <p className="text-[#1D3533]/60">
            The inbox feature is under development and will be available soon.
          </p>
        </div>
      </div>
    </div>
  );
}
