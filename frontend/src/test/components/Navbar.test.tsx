import { render, screen } from '@testing-library/react'
import { Navbar } from '@/components/Navbar'

describe('Navbar', () => {
  it('renders without crashing', () => {
    render(<Navbar />)
    expect(screen.getByRole('banner')).toBeInTheDocument()
  })

  it('renders the PawPoint logo image', () => {
    render(<Navbar />)
    expect(screen.getByAltText('PawPoint Logo')).toBeInTheDocument()
  })

  it('renders navigation links', () => {
    render(<Navbar />)
    expect(screen.getByRole('navigation')).toBeInTheDocument()
  })

  it('renders the Login link', () => {
    render(<Navbar />)
    expect(screen.getByRole('link', { name: 'Login' })).toBeInTheDocument()
  })

  it('renders the Signup link', () => {
    render(<Navbar />)
    expect(screen.getByRole('link', { name: 'Signup' })).toBeInTheDocument()
  })

  it('renders all nav item labels', () => {
    render(<Navbar />)
    expect(screen.getByRole('link', { name: 'Features' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'FAQ' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Pricing' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Demo' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'About Us' })).toBeInTheDocument()
  })

  it('Login link points to /login', () => {
    render(<Navbar />)
    const loginLink = screen.getByRole('link', { name: 'Login' })
    expect(loginLink).toHaveAttribute('href', '/login')
  })

  it('Signup link points to /signup', () => {
    render(<Navbar />)
    const signupLink = screen.getByRole('link', { name: 'Signup' })
    expect(signupLink).toHaveAttribute('href', '/signup')
  })
})
