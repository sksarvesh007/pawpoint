import '@testing-library/jest-dom'
import React from 'react'

// Mock next/navigation
vi.mock('next/navigation', () => ({
  usePathname: vi.fn(() => '/'),
  useRouter: vi.fn(() => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    prefetch: vi.fn(),
    refresh: vi.fn(),
  })),
  useSearchParams: vi.fn(() => new URLSearchParams()),
}))

// Mock next/image
vi.mock('next/image', () => ({
  default: ({ src, alt, width, height }: { src: string; alt: string; width?: number; height?: number }) =>
    React.createElement('img', { src, alt, width, height }),
}))

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ href, children, className }: { href: string; children: React.ReactNode; className?: string }) =>
    React.createElement('a', { href, className }, children),
}))

// Mock @sentry/nextjs
vi.mock('@sentry/nextjs', () => ({
  captureException: vi.fn(),
}))
