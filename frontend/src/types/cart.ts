export interface CartItem {
  id: number
  cart_id: number
  product_id: number
  quantity: number
  unit_price: number
  created_at: string
  product: {
    id: number
    title: string
    sku: string
    unit_size: string
    stock_quantity: number
    images: Array<{
      id: number
      url: string
      alt_text: string
    }>
  }
}

export interface Cart {
  id: number
  user_id: number
  coupon_code: string | null
  discount_amount: number
  created_at: string
  updated_at: string
  items: CartItem[]
  total_amount: number
  final_amount: number
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
