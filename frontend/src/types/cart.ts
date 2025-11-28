export interface CartItem {
  id: number
  cart_id: number
  product_id: number
  quantity: number
  unit_price: number
  product_title: string
  product_sku: string
  product_image_url: string | null
  product_stock_quantity: number
  subtotal: number
}

export interface Cart {
  id: number
  user_id: number
  coupon_code: string | null
  discount_amount: number
  subtotal: number
  total: number
  created_at: string
  updated_at: string
  items: CartItem[]
}

export interface AddToCartRequest {
  product_id: number
  quantity: number
}

export interface UpdateCartItemRequest {
  quantity: number
}

export interface ApplyCouponRequest {
  coupon_code: string
}

export interface CartValidation {
  is_valid: boolean
  errors: Array<{
    product_id: number
    message: string
  }>
}
