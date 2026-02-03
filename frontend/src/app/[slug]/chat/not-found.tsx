import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-white dark:bg-zinc-900">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-zinc-900 dark:text-white">
          404
        </h1>
        <p className="mt-4 text-xl text-zinc-600 dark:text-zinc-400">
          Clinic not found
        </p>
        <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-500">
          The clinic you're looking for doesn't exist or is no longer active.
        </p>
        <Link
          href="/"
          className="mt-6 inline-block rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
        >
          Go to Homepage
        </Link>
      </div>
    </div>
  );
}
