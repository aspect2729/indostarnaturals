import React from 'react'
import { Cart } from '../types/cart'

interface OrderSummaryProps {
  cart: Cart
  showItems?: boolean
}

const OrderSummary: React.FC<OrderSummaryProps> = ({ cart, showItems = true }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4">Order Summary</h2>

      {/* Items List */}
      {showItems && (
        <div className="space-y-3 mb-4 pb-4 border-b border-gray-200">
          {cart.items.map((item) => (
            <div key={item.id} className="flex justify-between text-sm">
              <div className="flex-1">
                <p className="font-medium text-gray-900">{item.product.title}</p>
                <p className="text-gray-600">
                  Qty: {item.quantity} × ₹{Number(item.unit_price).toFixed(2)}
                </p>
              </div>
              <p className="font-medium text-gray-900">
                ₹{(item.quantity * item.unit_price).toFixed(2)}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Price Breakdown */}
      <div className="space-y-2">
        <div className="flex justify-between text-gray-600">
          <span>Subtotal ({cart.items.length} items)</span>
          <span>₹{cart.total_amount.toFixed(2)}</span>
        </div>

        {cart.discount_amount > 0 && (
          <div className="flex justify-between text-green-600">
            <span>Discount</span>
            <span>-₹{cart.discount_amount.toFixed(2)}</span>
          </div>
        )}

        {cart.coupon_code && (
          <div className="flex justify-between text-sm text-gray-600">
            <span>Coupon Applied</span>
            <span className="font-medium">{cart.coupon_code}</span>
          </div>
        )}
      </div>

      {/* Divider */}
      <div className="border-t border-gray-200 my-4"></div>

      {/* Total */}
      <div className="flex justify-between text-lg font-bold text-gray-900">
        <span>Total Amount</span>
        <span>₹{cart.final_amount.toFixed(2)}</span>
      </div>

      {/* Tax Note */}
      <p className="text-xs text-gray-500 mt-2">
        Inclusive of all taxes
      </p>
    </div>
  )
}

export default OrderSummary
