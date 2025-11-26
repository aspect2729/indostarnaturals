export enum UserRole {
  CONSUMER = 'consumer',
  DISTRIBUTOR = 'distributor',
  OWNER = 'owner',
}

export interface Address {
  id: number
  user_id: number
  name: string
  phone: string
  address_line1: string
  address_line2: string | null
  city: string
  state: string
  postal_code: string
  country: string
  is_default: boolean
  created_at: string
  updated_at: string
}

export interface UpdateUserRequest {
  name?: string
  email?: string
  phone?: string
}

export interface CreateAddressRequest {
  name: string
  phone: string
  address_line1: string
  address_line2?: string
  city: string
  state: string
  postal_code: string
  country: string
  is_default?: boolean
}

export interface UpdateAddressRequest extends Partial<CreateAddressRequest> {}
