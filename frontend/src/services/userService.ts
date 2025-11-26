import api from './api'
import { User } from '../types/auth'
import { Address, UpdateUserRequest, CreateAddressRequest, UpdateAddressRequest } from '../types/user'

const userService = {
  // Get current user profile
  getProfile: async (): Promise<User> => {
    const response = await api.get('/api/v1/users/me')
    return response.data
  },

  // Update user profile
  updateProfile: async (data: UpdateUserRequest): Promise<User> => {
    const response = await api.put('/api/v1/users/me', data)
    return response.data
  },

  // Get user addresses
  getAddresses: async (): Promise<Address[]> => {
    const response = await api.get('/api/v1/users/me/addresses')
    return response.data
  },

  // Create new address
  createAddress: async (data: CreateAddressRequest): Promise<Address> => {
    const response = await api.post('/api/v1/users/me/addresses', data)
    return response.data
  },

  // Update address
  updateAddress: async (id: number, data: UpdateAddressRequest): Promise<Address> => {
    const response = await api.put(`/api/v1/users/me/addresses/${id}`, data)
    return response.data
  },

  // Delete address
  deleteAddress: async (id: number): Promise<void> => {
    await api.delete(`/api/v1/users/me/addresses/${id}`)
  },
}

export default userService
