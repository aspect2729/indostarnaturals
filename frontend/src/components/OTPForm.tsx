import React, { useState } from 'react'
import { useFormik } from 'formik'
import * as Yup from 'yup'
import { useAuth } from '../hooks/useAuth'
import authService from '../services/authService'

interface OTPFormProps {
  onSuccess?: () => void
  mode?: 'phone' | 'email'
}

const OTPForm: React.FC<OTPFormProps> = ({ onSuccess, mode = 'phone' }) => {
  const { login } = useAuth()
  const [step, setStep] = useState<'input' | 'verify'>('input')
  const [identifier, setIdentifier] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Step 1: Input phone/email
  const inputFormik = useFormik({
    initialValues: {
      value: '',
    },
    validationSchema: Yup.object({
      value:
        mode === 'phone'
          ? Yup.string()
              .matches(/^\+?[1-9]\d{1,14}$/, 'Invalid phone number format')
              .required('Phone number is required')
          : Yup.string().email('Invalid email address').required('Email is required'),
    }),
    onSubmit: async (values) => {
      setIsLoading(true)
      setError(null)

      try {
        const data = mode === 'phone' ? { phone: values.value } : { email: values.value }
        await authService.sendOTP(data)
        setIdentifier(values.value)
        setStep('verify')
      } catch (err: any) {
        setError(err.response?.data?.error?.message || 'Failed to send OTP')
      } finally {
        setIsLoading(false)
      }
    },
  })

  // Step 2: Verify OTP
  const verifyFormik = useFormik({
    initialValues: {
      otp: '',
    },
    validationSchema: Yup.object({
      otp: Yup.string()
        .matches(/^\d{6}$/, 'OTP must be 6 digits')
        .required('OTP is required'),
    }),
    onSubmit: async (values) => {
      setIsLoading(true)
      setError(null)

      try {
        const data =
          mode === 'phone'
            ? { phone: identifier, otp: values.otp }
            : { email: identifier, otp: values.otp }
        await login(data)
        onSuccess?.()
      } catch (err: any) {
        setError(err.response?.data?.error?.message || 'Invalid OTP')
      } finally {
        setIsLoading(false)
      }
    },
  })

  const handleResendOTP = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const data = mode === 'phone' ? { phone: identifier } : { email: identifier }
      await authService.sendOTP(data)
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to resend OTP')
    } finally {
      setIsLoading(false)
    }
  }

  if (step === 'input') {
    return (
      <form onSubmit={inputFormik.handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="value" className="block text-sm font-medium text-gray-700">
            {mode === 'phone' ? 'Phone Number' : 'Email Address'}
          </label>
          <input
            id="value"
            type={mode === 'phone' ? 'tel' : 'email'}
            placeholder={mode === 'phone' ? '+1234567890' : 'you@example.com'}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-3 py-2 border"
            {...inputFormik.getFieldProps('value')}
          />
          {inputFormik.touched.value && inputFormik.errors.value && (
            <p className="mt-1 text-sm text-red-600">{inputFormik.errors.value}</p>
          )}
        </div>

        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Sending...' : 'Send OTP'}
        </button>
      </form>
    )
  }

  return (
    <form onSubmit={verifyFormik.handleSubmit} className="space-y-4">
      <div>
        <p className="text-sm text-gray-600 mb-4">
          We've sent a 6-digit code to{' '}
          <span className="font-medium text-gray-900">{identifier}</span>
        </p>

        <label htmlFor="otp" className="block text-sm font-medium text-gray-700">
          Enter OTP
        </label>
        <input
          id="otp"
          type="text"
          maxLength={6}
          placeholder="123456"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-3 py-2 border"
          {...verifyFormik.getFieldProps('otp')}
        />
        {verifyFormik.touched.otp && verifyFormik.errors.otp && (
          <p className="mt-1 text-sm text-red-600">{verifyFormik.errors.otp}</p>
        )}
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <button
        type="submit"
        disabled={isLoading}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? 'Verifying...' : 'Verify OTP'}
      </button>

      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => setStep('input')}
          className="text-sm text-primary-600 hover:text-primary-500"
        >
          Change {mode === 'phone' ? 'phone number' : 'email'}
        </button>
        <button
          type="button"
          onClick={handleResendOTP}
          disabled={isLoading}
          className="text-sm text-primary-600 hover:text-primary-500 disabled:opacity-50"
        >
          Resend OTP
        </button>
      </div>
    </form>
  )
}

export default OTPForm
