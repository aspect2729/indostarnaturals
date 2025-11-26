import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import OTPForm from '../components/OTPForm'
import GoogleSignInButton from '../components/GoogleSignInButton'

const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { isAuthenticated } = useAuth()

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      const from = (location.state as any)?.from?.pathname || '/'
      // Only navigate if we're not already on the target page
      if (location.pathname !== from) {
        navigate(from, { replace: true })
      }
    }
  }, [isAuthenticated, navigate, location])

  const handleSuccess = () => {
    const from = (location.state as any)?.from?.pathname || '/'
    navigate(from, { replace: true })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Welcome to IndoStar Naturals
          </p>
        </div>

        <div className="mt-8 bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="space-y-6">
            <OTPForm mode="phone" onSuccess={handleSuccess} />

            {import.meta.env.VITE_GOOGLE_CLIENT_ID && (
              <>
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-gray-500">Or continue with</span>
                  </div>
                </div>

                <GoogleSignInButton onSuccess={handleSuccess} />
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
