import React, { createContext, useState, useEffect, useCallback, ReactNode } from 'react'
import { User, AuthState } from '../types/auth'
import authService, { VerifyOTPRequest } from '../services/authService'
import { tokenStorage } from '../services/api'

interface AuthContextType extends AuthState {
  login: (data: VerifyOTPRequest) => Promise<void>
  loginWithGoogle: (token: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Check if user is authenticated on mount
  useEffect(() => {
    const initAuth = async () => {
      const accessToken = tokenStorage.getAccessToken()
      
      if (accessToken) {
        try {
          // Fetch current user profile
          const userData = await authService.getCurrentUser()
          setUser(userData)
        } catch (error) {
          console.error('Failed to fetch user:', error)
          // Clear invalid tokens
          tokenStorage.clearTokens()
          setUser(null)
        }
      }
      
      // Always set loading to false, even if there's no token
      setIsLoading(false)
    }

    initAuth()
  }, [])

  // Login with OTP
  const login = useCallback(async (data: VerifyOTPRequest) => {
    try {
      const authResponse = await authService.verifyOTP(data)
      setUser(authResponse.user)
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }, [])

  // Login with Google
  const loginWithGoogle = useCallback(async (token: string) => {
    try {
      const authResponse = await authService.googleAuth({ token })
      setUser(authResponse.user)
    } catch (error) {
      console.error('Google login failed:', error)
      throw error
    }
  }, [])

  // Logout
  const logout = useCallback(() => {
    authService.logout()
    setUser(null)
  }, [])

  // Refresh user data
  const refreshUser = useCallback(async () => {
    try {
      const userData = await authService.getCurrentUser()
      setUser(userData)
    } catch (error) {
      console.error('Failed to refresh user:', error)
      throw error
    }
  }, [])

  const value: AuthContextType = {
    user,
    tokens: tokenStorage.getAccessToken()
      ? {
          access_token: tokenStorage.getAccessToken()!,
          refresh_token: tokenStorage.getRefreshToken()!,
          token_type: 'bearer',
        }
      : null,
    isAuthenticated: !!user,
    isLoading,
    login,
    loginWithGoogle,
    logout,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
