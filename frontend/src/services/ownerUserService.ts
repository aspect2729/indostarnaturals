import api from './api'
import { UserRole } from '../types/user'

export enum DistributorStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
}

export interface UserResponse {
  id: number
  email: string | null
  phone: string
  name: string
  role: UserRole
  distributor_status: DistributorStatus | null
  is_email_verified: boolean
  is_phone_verified: boolean
  is_active: boolean
}

export interface UserFilters {
  role_filter?: UserRole
  status_filter?: boolean
  distributor_status_filter?: DistributorStatus
}

export interface UserRoleUpdate {
  role: UserRole
}

export const ownerUserService = {
  /**
   * Get all users with filtering (owner only)
   */
  getAllUsers: async (filters?: UserFilters): Promise<UserResponse[]> => {
    const params = new URLSearchParams()
    
    if (filters?.role_filter) params.append('role_filter', filters.role_filter)
    if (filters?.status_filter !== undefined) params.append('status_filter', filters.status_filter.toString())
    if (filters?.distributor_status_filter) params.append('distributor_status_filter', filters.distributor_status_filter)
    
    const response = await api.get<UserResponse[]>(
      `/api/v1/owner/users?${params.toString()}`
    )
    return response.data
  },

  /**
   * Update user role (owner only)
   */
  updateUserRole: async (
    userId: number,
    roleUpdate: UserRoleUpdate
  ): Promise<UserResponse> => {
    const response = await api.put<UserResponse>(
      `/api/v1/owner/users/${userId}/role`,
      roleUpdate
    )
    return response.data
  },
}
