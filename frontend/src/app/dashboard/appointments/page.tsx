/**
 * Appointments page - placeholder for future implementation.
 */

import { Calendar } from "lucide-react";

export default function AppointmentsPage() {
  return (
    <div className="max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-nunito font-bold text-zinc-900 flex items-center gap-3">
          <Calendar className="w-8 h-8 text-teal-600" />
          Appointments
        </h1>
        <p className="text-zinc-600 mt-1">
          View and manage your clinic&apos;s appointments
        </p>
      </div>

      <div className="bg-white rounded-xl border border-zinc-200 p-12 shadow-sm text-center">
        <Calendar className="w-16 h-16 text-zinc-300 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-zinc-900 mb-2">
          Coming Soon
        </h2>
        <p className="text-zinc-600">
          Appointment calendar and management features will be available here.
        </p>
      </div>
    </div>
  );
}
