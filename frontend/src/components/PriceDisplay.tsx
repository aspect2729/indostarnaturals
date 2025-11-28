import React from 'react'
import { useAuth } from '../hooks/useAuth'
import { UserRole } from '../types/auth'

interface PriceDisplayProps {
  consumerPrice: number
  distributorPrice: number
  className?: string
  showLabel?: boolean
}

const PriceDisplay: React.FC<PriceDisplayProps> = ({
  consumerPrice,
  distributorPrice,
  className = '',
  showLabel = false,
}) => {
  const { user } = useAuth()

  // Determine which price to show based on user role
  const price = user?.role === UserRole.DISTRIBUTOR ? distributorPrice : consumerPrice
  const priceLabel = user?.role === UserRole.DISTRIBUTOR ? 'Distributor Price' : 'Price'

  // Format price to 2 decimal places - convert to number if it's a string
  const numericPrice = typeof price === 'string' ? parseFloat(price) : price
  const formattedPrice = `₹${numericPrice.toFixed(2)}`

  return (
    <div className={`price-display ${className}`}>
      {showLabel && <span className="text-sm text-gray-600 mr-2">{priceLabel}:</span>}
      <span className="text-lg font-semibold text-gray-900">{formattedPrice}</span>
    </div>
  )
}

export default PriceDisplay
