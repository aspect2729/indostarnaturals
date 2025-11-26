/**
 * Unit tests for AuthModal component
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '../utils/test-utils'
import AuthModal from '../../components/AuthModal'

describe('AuthModal', () => {
  it('renders login form by default', () => {
    render(<AuthModal isOpen={true} onClose={() => {}} />)
    
    expect(screen.getByText(/sign in/i)).toBeInTheDocument()
  })

  it('switches to signup form when clicking signup tab', async () => {
    render(<AuthModal isOpen={true} onClose={() => {}} />)
    
    const signupTab = screen.getByText(/sign up/i)
    fireEvent.click(signupTab)
    
    await waitFor(() => {
      expect(screen.getByText(/create account/i)).toBeInTheDocument()
    })
  })

  it('calls onClose when close button is clicked', () => {
    const onClose = vi.fn()
    render(<AuthModal isOpen={true} onClose={onClose} />)
    
    const closeButton = screen.getByRole('button', { name: /close/i })
    fireEvent.click(closeButton)
    
    expect(onClose).toHaveBeenCalled()
  })

  it('does not render when isOpen is false', () => {
    const { container } = render(<AuthModal isOpen={false} onClose={() => {}} />)
    
    expect(container.firstChild).toBeNull()
  })
})
