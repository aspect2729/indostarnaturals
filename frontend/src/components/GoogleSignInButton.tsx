import React, { useEffect, useState } from 'react'
import { useAuth } from '../hooks/useAuth'

interface GoogleSignInButtonProps {
  onSuccess?: () => void
  onError?: (error: Error) => void
}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: any) => void
          renderButton: (element: HTMLElement, config: any) => void
          prompt: () => void
        }
      }
    }
  }
}

const GoogleSignInButton: React.FC<GoogleSignInButtonProps> = ({ onSuccess, onError }) => {
  const { loginWithGoogle } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [isConfigured, setIsConfigured] = useState(true)
  const buttonRef = React.useRef<HTMLDivElement>(null)

  useEffect(() => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

    if (!clientId) {
      setIsConfigured(false)
      return
    }

    // Load Google Sign-In script
    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    document.body.appendChild(script)

    script.onload = () => {
      if (window.google && buttonRef.current) {
        window.google.accounts.id.initialize({
          client_id: clientId,
          callback: handleCredentialResponse,
        })

        window.google.accounts.id.renderButton(buttonRef.current, {
          theme: 'outline',
          size: 'large',
          width: buttonRef.current.offsetWidth,
          text: 'continue_with',
        })
      }
    }

    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script)
      }
    }
  }, [])

  const handleCredentialResponse = async (response: any) => {
    setIsLoading(true)

    try {
      await loginWithGoogle(response.credential)
      onSuccess?.()
    } catch (error) {
      console.error('Google sign-in failed:', error)
      onError?.(error as Error)
    } finally {
      setIsLoading(false)
    }
  }

  // Don't render anything if Google OAuth is not configured
  if (!isConfigured) {
    return (
      <div className="w-full p-3 bg-gray-100 rounded text-center text-sm text-gray-600">
        Google Sign-In not configured
      </div>
    )
  }

  return (
    <div className="w-full">
      <div ref={buttonRef} className="w-full" />
      {isLoading && (
        <div className="mt-2 text-center">
          <span className="text-sm text-gray-600">Signing in...</span>
        </div>
      )}
      <div className="mt-2 text-xs text-gray-500 text-center">
        Note: If you see a 403 error, add http://localhost:5173 to authorized origins in Google Cloud Console
      </div>
    </div>
  )
}

export default GoogleSignInButton
