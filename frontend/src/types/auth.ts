export enum UserRole {
  CONSUMER = 'consumer',
  DISTRIBUTOR = 'distributor',
  OWNER = 'owner',
}

export interface User {
  id: number
  email: string | null
  phone: string
  name: string
  role: UserRole
  is_email_verified: boolean
  is_phone_verified: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface AuthState {
  user: User | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  isLoading: boolean
}
