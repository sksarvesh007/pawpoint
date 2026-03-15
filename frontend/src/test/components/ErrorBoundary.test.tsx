import { render, screen } from '@testing-library/react'
import { ErrorBoundary } from '@/components/ErrorBoundary'

// Suppress React's error boundary console.error output during tests
const originalConsoleError = console.error
beforeEach(() => {
  console.error = vi.fn()
})
afterEach(() => {
  console.error = originalConsoleError
})

function ThrowingChild({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test error')
  }
  return <div>Child content rendered successfully</div>
}

describe('ErrorBoundary', () => {
  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <ThrowingChild shouldThrow={false} />
      </ErrorBoundary>
    )
    expect(screen.getByText('Child content rendered successfully')).toBeInTheDocument()
  })

  it('shows default fallback UI when a child throws', () => {
    render(
      <ErrorBoundary>
        <ThrowingChild shouldThrow={true} />
      </ErrorBoundary>
    )
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    expect(screen.getByText('We encountered an error loading the dashboard')).toBeInTheDocument()
  })

  it('shows a Reload Page button in the default fallback', () => {
    render(
      <ErrorBoundary>
        <ThrowingChild shouldThrow={true} />
      </ErrorBoundary>
    )
    expect(screen.getByRole('button', { name: 'Reload Page' })).toBeInTheDocument()
  })

  it('renders a custom fallback when provided and a child throws', () => {
    render(
      <ErrorBoundary fallback={<div>Custom fallback UI</div>}>
        <ThrowingChild shouldThrow={true} />
      </ErrorBoundary>
    )
    expect(screen.getByText('Custom fallback UI')).toBeInTheDocument()
    expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument()
  })

  it('does not render fallback when there is no error', () => {
    render(
      <ErrorBoundary fallback={<div>Custom fallback UI</div>}>
        <ThrowingChild shouldThrow={false} />
      </ErrorBoundary>
    )
    expect(screen.queryByText('Custom fallback UI')).not.toBeInTheDocument()
    expect(screen.getByText('Child content rendered successfully')).toBeInTheDocument()
  })
})
