import React, { useState } from 'react'
import OTPForm from './OTPForm'
import GoogleSignInButton from './GoogleSignInButton'

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
}

type AuthTab = 'login' | 'signup'
type AuthMethod = 'phone' | 'email'

const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<AuthTab>('login')
  const [authMethod, setAuthMethod] = useState<AuthMethod>('phone')

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          onClick={onClose}
        />

        {/* Modal panel */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          {/* Header */}
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-2xl font-bold text-gray-900">
                {activeTab === 'login' ? 'Welcome Back' : 'Create Account'}
              </h3>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-500 focus:outline-none"
              >
                <span className="sr-only">Close</span>
                <svg
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-gray-200 mb-6">
              <button
                className={`flex-1 py-2 px-4 text-center font-medium ${
                  activeTab === 'login'
                    ? 'border-b-2 border-primary-600 text-primary-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
                onClick={() => setActiveTab('login')}
              >
                Login
              </button>
              <button
                className={`flex-1 py-2 px-4 text-center font-medium ${
                  activeTab === 'signup'
                    ? 'border-b-2 border-primary-600 text-primary-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
                onClick={() => setActiveTab('signup')}
              >
                Sign Up
              </button>
            </div>

            {/* Tab content */}
            <div className="space-y-4">
              {/* Auth method selector */}
              <div className="flex gap-2">
                <button
                  className={`flex-1 py-2 px-4 rounded-md text-sm font-medium ${
                    authMethod === 'phone'
                      ? 'bg-primary-100 text-primary-700 border-2 border-primary-600'
                      : 'bg-gray-100 text-gray-700 border-2 border-transparent'
                  }`}
                  onClick={() => setAuthMethod('phone')}
                >
                  Phone
                </button>
                <button
                  className={`flex-1 py-2 px-4 rounded-md text-sm font-medium ${
                    authMethod === 'email'
                      ? 'bg-primary-100 text-primary-700 border-2 border-primary-600'
                      : 'bg-gray-100 text-gray-700 border-2 border-transparent'
                  }`}
                  onClick={() => setAuthMethod('email')}
                >
                  Email
                </button>
              </div>

              {/* OTP Form */}
              <OTPForm mode={authMethod} onSuccess={onClose} />

              {/* Divider */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">Or continue with</span>
                </div>
              </div>

              {/* Google Sign In */}
              <GoogleSignInButton onSuccess={onClose} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AuthModal
