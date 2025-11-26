import api from './api'
import {
  Cart,
  AddToCartRequest,
  UpdateCartItemRequest,
  ApplyCouponRequest,
  CartValidation,
} from '../types/cart'

export const cartService = {
  /**
   * Get the current user's cart
   */
  getCart: async (): Promise<Cart> => {
    const response = await api.get<Cart>('/api/v1/cart')
    return response.data
  },

  /**
   * Add an item to the cart
   */
  addItem: async (data: AddToCartRequest): Promise<Cart> => {
    const response = await api.post<Cart>('/api/v1/cart/items', data)
    return response.data
  },

  /**
   * Update cart item quantity
   */
  updateItemQuantity: async (
    itemId: number,
    data: UpdateCartItemRequest
  ): Promise<Cart> => {
    const response = await api.put<Cart>(`/api/v1/cart/items/${itemId}`, data)
    return response.data
  },

  /**
   * Remove an item from the cart
   */
  removeItem: async (itemId: number): Promise<Cart> => {
    const response = await api.delete<Cart>(`/api/v1/cart/items/${itemId}`)
    return response.data
  },

  /**
   * Apply a coupon code to the cart
   */
  applyCoupon: async (data: ApplyCouponRequest): Promise<Cart> => {
    const response = await api.post<Cart>('/api/v1/cart/coupon', data)
    return response.data
  },

  /**
   * Remove the coupon from the cart
   */
  removeCoupon: async (): Promise<Cart> => {
    const response = await api.delete<Cart>('/api/v1/cart/coupon')
    return response.data
  },

  /**
   * Validate the cart before checkout
   */
  validateCart: async (): Promise<CartValidation> => {
    const response = await api.get<CartValidation>('/api/v1/cart/validate')
    return response.data
  },
}
