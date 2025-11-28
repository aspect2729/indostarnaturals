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
  const [hasError, setHasError] = useState(false)
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
        try {
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
        } catch (error) {
          console.error('Failed to initialize Google Sign-In:', error)
          setHasError(true)
        }
      }
    }

    script.onerror = () => {
      console.error('Failed to load Google Sign-In script')
      setHasError(true)
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

  // Don't render if not configured
  if (!isConfigured) {
    return (
      <div className="w-full p-3 bg-gray-100 rounded text-center text-sm text-gray-600">
        Google Sign-In not configured
      </div>
    )
  }

  // Show error state with helpful message
  if (hasError) {
    return (
      <div className="w-full p-4 bg-yellow-50 border border-yellow-200 rounded">
        <p className="text-sm text-yellow-800 font-medium mb-2 text-center">
          ⚠️ Google Sign-In Configuration Required
        </p>
        <p className="text-xs text-yellow-700 mb-2">
          To use Google Sign-In, add <code className="bg-yellow-100 px-1 rounded">http://localhost:5173</code> to 
          "Authorized JavaScript origins" in your Google Cloud Console OAuth client settings.
        </p>
        <p className="text-xs text-yellow-600 text-center">
          <strong>Use Phone (OTP) authentication below instead</strong>
        </p>
      </div>
    )
  }

  return (
    <div className="w-full">
      <div ref={buttonRef} className="w-full min-h-[40px]" />
      {isLoading && (
        <div className="mt-2 text-center">
          <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900 mr-2"></div>
          <span className="text-sm text-gray-600">Signing in with Google...</span>
        </div>
      )}
    </div>
  )
}

export default GoogleSignInButton
