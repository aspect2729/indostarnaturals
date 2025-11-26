import api, { tokenStorage } from './api'
import { User, AuthTokens } from '../types/auth'

export interface SendOTPRequest {
  phone?: string
  email?: string
}

export interface VerifyOTPRequest {
  phone?: string
  email?: string
  otp: string
}

export interface GoogleAuthRequest {
  token: string
}

export interface ResetPasswordRequest {
  email: string
}

export interface CompletePasswordResetRequest {
  token: string
  new_password: string
}

export interface AuthResponse {
  user: User
  access_token: string
  refresh_token: string
  token_type: string
}

const authService = {
  // Send OTP to phone or email
  sendOTP: async (data: SendOTPRequest): Promise<{ message: string }> => {
    const response = await api.post('/api/v1/auth/send-otp', data)
    return response.data
  },

  // Verify OTP and get JWT tokens
  verifyOTP: async (data: VerifyOTPRequest): Promise<AuthResponse> => {
    const response = await api.post('/api/v1/auth/verify-otp', data)
    const authData = response.data
    
    // Store tokens
    tokenStorage.setTokens(authData.access_token, authData.refresh_token)
    
    return authData
  },

  // Google OAuth authentication
  googleAuth: async (data: GoogleAuthRequest): Promise<AuthResponse> => {
    const response = await api.post('/api/v1/auth/google', data)
    const authData = response.data
    
    // Store tokens
    tokenStorage.setTokens(authData.access_token, authData.refresh_token)
    
    return authData
  },

  // Refresh JWT token
  refreshToken: async (refreshToken: string): Promise<AuthTokens> => {
    const response = await api.post('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    })
    const tokens = response.data
    
    // Store new tokens
    tokenStorage.setTokens(tokens.access_token, tokens.refresh_token)
    
    return tokens
  },

  // Request password reset
  requestPasswordReset: async (data: ResetPasswordRequest): Promise<{ message: string }> => {
    const response = await api.post('/api/v1/auth/reset-password', data)
    return response.data
  },

  // Complete password reset
  completePasswordReset: async (data: CompletePasswordResetRequest): Promise<{ message: string }> => {
    const response = await api.put('/api/v1/auth/reset-password', data)
    return response.data
  },

  // Get current user profile
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/api/v1/users/me')
    return response.data
  },

  // Logout (clear tokens)
  logout: (): void => {
    tokenStorage.clearTokens()
  },
}

export default authService
