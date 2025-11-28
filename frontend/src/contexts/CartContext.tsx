import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { Cart, AddToCartRequest } from '../types/cart'
import { cartService } from '../services/cartService'
import { useAuth } from '../hooks/useAuth'

interface CartContextType {
  cart: Cart | null
  isLoading: boolean
  error: string | null
  itemCount: number
  addToCart: (data: AddToCartRequest) => Promise<void>
  updateItemQuantity: (itemId: number, quantity: number) => Promise<void>
  removeItem: (itemId: number) => Promise<void>
  applyCoupon: (couponCode: string) => Promise<void>
  removeCoupon: () => Promise<void>
  refreshCart: () => Promise<void>
  clearError: () => void
}

const CartContext = createContext<CartContextType | undefined>(undefined)

export const CartProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [cart, setCart] = useState<Cart | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { isAuthenticated } = useAuth()

  // Calculate total item count
  const itemCount = cart?.items.reduce((sum, item) => sum + item.quantity, 0) || 0

  // Fetch cart data
  const fetchCart = useCallback(async () => {
    if (!isAuthenticated) {
      setCart(null)
      return
    }

    try {
      setIsLoading(true)
      setError(null)
      const cartData = await cartService.getCart()
      setCart(cartData)
    } catch (err: any) {
      console.error('Failed to fetch cart:', err)
      setError(err.response?.data?.error?.message || 'Failed to load cart')
    } finally {
      setIsLoading(false)
    }
  }, [isAuthenticated])

  // Load cart on mount and when authentication changes
  useEffect(() => {
    fetchCart()
  }, [fetchCart])

  // Add item to cart with optimistic update
  const addToCart = async (data: AddToCartRequest) => {
    // Check if user is authenticated
    if (!isAuthenticated) {
      const error = 'Please log in to add items to cart'
      setError(error)
      throw new Error(error)
    }

    try {
      setError(null)
      
      // Optimistic update: add item to local state
      if (cart) {
        const existingItem = cart.items.find(item => item.product_id === data.product_id)
        
        if (existingItem) {
          // Update quantity of existing item
          const optimisticCart = {
            ...cart,
            items: cart.items.map(item =>
              item.product_id === data.product_id
                ? { ...item, quantity: item.quantity + data.quantity }
                : item
            ),
          }
          setCart(optimisticCart)
        }
      }

      // Make API call
      const updatedCart = await cartService.addItem(data)
      setCart(updatedCart)
    } catch (err: any) {
      console.error('Failed to add item to cart:', err)
      const errorMessage = err.response?.data?.detail || err.response?.data?.error?.message || err.message || 'Failed to add item to cart'
      setError(errorMessage)
      // Revert optimistic update by refetching
      await fetchCart()
      throw err
    }
  }

  // Update item quantity with optimistic update
  const updateItemQuantity = async (itemId: number, quantity: number) => {
    if (!cart) return

    const previousCart = cart

    try {
      setError(null)
      
      // Optimistic update
      const optimisticCart = {
        ...cart,
        items: cart.items.map(item =>
          item.id === itemId ? { ...item, quantity } : item
        ),
      }
      setCart(optimisticCart)

      // Make API call
      const updatedCart = await cartService.updateItemQuantity(itemId, { quantity })
      setCart(updatedCart)
    } catch (err: any) {
      console.error('Failed to update item quantity:', err)
      const errorMessage = err.response?.data?.detail || err.response?.data?.error?.message || err.message || 'Failed to update quantity'
      setError(errorMessage)
      // Revert optimistic update
      setCart(previousCart)
      throw err
    }
  }

  // Remove item with optimistic update
  const removeItem = async (itemId: number) => {
    if (!cart) return

    const previousCart = cart

    try {
      setError(null)
      
      // Optimistic update
      const optimisticCart = {
        ...cart,
        items: cart.items.filter(item => item.id !== itemId),
      }
      setCart(optimisticCart)

      // Make API call
      const updatedCart = await cartService.removeItem(itemId)
      setCart(updatedCart)
    } catch (err: any) {
      console.error('Failed to remove item:', err)
      const errorMessage = err.response?.data?.detail || err.response?.data?.error?.message || err.message || 'Failed to remove item'
      setError(errorMessage)
      // Revert optimistic update
      setCart(previousCart)
      throw err
    }
  }

  // Apply coupon
  const applyCoupon = async (couponCode: string) => {
    try {
      setError(null)
      const updatedCart = await cartService.applyCoupon({ coupon_code: couponCode })
      setCart(updatedCart)
    } catch (err: any) {
      console.error('Failed to apply coupon:', err)
      const errorMessage = err.response?.data?.detail || err.response?.data?.error?.message || err.message || 'Failed to apply coupon'
      setError(errorMessage)
      throw err
    }
  }

  // Remove coupon
  const removeCoupon = async () => {
    try {
      setError(null)
      const updatedCart = await cartService.removeCoupon()
      setCart(updatedCart)
    } catch (err: any) {
      console.error('Failed to remove coupon:', err)
      const errorMessage = err.response?.data?.detail || err.response?.data?.error?.message || err.message || 'Failed to remove coupon'
      setError(errorMessage)
      throw err
    }
  }

  // Refresh cart
  const refreshCart = async () => {
    await fetchCart()
  }

  // Clear error
  const clearError = () => {
    setError(null)
  }

  const value: CartContextType = {
    cart,
    isLoading,
    error,
    itemCount,
    addToCart,
    updateItemQuantity,
    removeItem,
    applyCoupon,
    removeCoupon,
    refreshCart,
    clearError,
  }

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}

export const useCart = (): CartContextType => {
  const context = useContext(CartContext)
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider')
  }
  return context
}
