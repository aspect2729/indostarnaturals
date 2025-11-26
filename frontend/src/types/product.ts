export interface Product {
  id: number
  owner_id: number
  title: string
  description: string
  category_id: number
  sku: string
  unit_size: string
  consumer_price: number
  distributor_price: number
  stock_quantity: number
  is_subscription_available: boolean
  is_active: boolean
  created_at: string
  updated_at: string
  images: ProductImage[]
  category: Category
}

export interface ProductImage {
  id: number
  product_id: number
  url: string
  alt_text: string
  display_order: number
  created_at: string
}

export interface Category {
  id: number
  name: string
  slug: string
  parent_id: number | null
  display_order: number
}

export interface ProductFilters {
  category_id?: number
  min_price?: number
  max_price?: number
  search?: string
  is_subscription_available?: boolean
  page?: number
  page_size?: number
  sort_by?: 'price_asc' | 'price_desc' | 'name_asc' | 'name_desc' | 'newest'
}

export interface PaginatedProducts {
  items: Product[]
  total: number
  page: number
  page_size: number
  total_pages: number
}
