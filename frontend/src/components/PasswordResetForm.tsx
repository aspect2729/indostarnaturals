import React, { useState } from 'react'
import { useFormik } from 'formik'
import * as Yup from 'yup'
import authService from '../services/authService'

interface PasswordResetFormProps {
  token?: string
  onSuccess?: () => void
}

const PasswordResetForm: React.FC<PasswordResetFormProps> = ({ token, onSuccess }) => {
  const [step] = useState<'request' | 'complete'>(token ? 'complete' : 'request')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  // Step 1: Request password reset
  const requestFormik = useFormik({
    initialValues: {
      email: '',
    },
    validationSchema: Yup.object({
      email: Yup.string().email('Invalid email address').required('Email is required'),
    }),
    onSubmit: async (values) => {
      setIsLoading(true)
      setError(null)
      setSuccessMessage(null)

      try {
        const response = await authService.requestPasswordReset(values)
        setSuccessMessage(response.message || 'Password reset link sent to your email')
      } catch (err: any) {
        setError(err.response?.data?.error?.message || 'Failed to send reset link')
      } finally {
        setIsLoading(false)
      }
    },
  })

  // Step 2: Complete password reset
  const completeFormik = useFormik({
    initialValues: {
      new_password: '',
      confirm_password: '',
    },
    validationSchema: Yup.object({
      new_password: Yup.string()
        .min(8, 'Password must be at least 8 characters')
        .matches(
          /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
          'Password must contain uppercase, lowercase, and number'
        )
        .required('Password is required'),
      confirm_password: Yup.string()
        .oneOf([Yup.ref('new_password')], 'Passwords must match')
        .required('Please confirm your password'),
    }),
    onSubmit: async (values) => {
      if (!token) {
        setError('Invalid reset token')
        return
      }

      setIsLoading(true)
      setError(null)
      setSuccessMessage(null)

      try {
        const response = await authService.completePasswordReset({
          token,
          new_password: values.new_password,
        })
        setSuccessMessage(response.message || 'Password reset successful')
        setTimeout(() => {
          onSuccess?.()
        }, 2000)
      } catch (err: any) {
        setError(err.response?.data?.error?.message || 'Failed to reset password')
      } finally {
        setIsLoading(false)
      }
    },
  })

  if (step === 'request') {
    return (
      <div className="max-w-md mx-auto">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Reset Password</h2>
        <p className="text-sm text-gray-600 mb-6">
          Enter your email address and we'll send you a link to reset your password.
        </p>

        <form onSubmit={requestFormik.handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              placeholder="you@example.com"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-3 py-2 border"
              {...requestFormik.getFieldProps('email')}
            />
            {requestFormik.touched.email && requestFormik.errors.email && (
              <p className="mt-1 text-sm text-red-600">{requestFormik.errors.email}</p>
            )}
          </div>

          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {successMessage && (
            <div className="rounded-md bg-green-50 p-4">
              <p className="text-sm text-green-800">{successMessage}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>
      </div>
    )
  }

  return (
    <div className="max-w-md mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Create New Password</h2>
      <p className="text-sm text-gray-600 mb-6">
        Enter your new password below. Make sure it's strong and secure.
      </p>

      <form onSubmit={completeFormik.handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="new_password" className="block text-sm font-medium text-gray-700">
            New Password
          </label>
          <input
            id="new_password"
            type="password"
            placeholder="••••••••"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-3 py-2 border"
            {...completeFormik.getFieldProps('new_password')}
          />
          {completeFormik.touched.new_password && completeFormik.errors.new_password && (
            <p className="mt-1 text-sm text-red-600">{completeFormik.errors.new_password}</p>
          )}
        </div>

        <div>
          <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700">
            Confirm Password
          </label>
          <input
            id="confirm_password"
            type="password"
            placeholder="••••••••"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-3 py-2 border"
            {...completeFormik.getFieldProps('confirm_password')}
          />
          {completeFormik.touched.confirm_password && completeFormik.errors.confirm_password && (
            <p className="mt-1 text-sm text-red-600">{completeFormik.errors.confirm_password}</p>
          )}
        </div>

        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {successMessage && (
          <div className="rounded-md bg-green-50 p-4">
            <p className="text-sm text-green-800">{successMessage}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Resetting...' : 'Reset Password'}
        </button>
      </form>
    </div>
  )
}

export default PasswordResetForm
