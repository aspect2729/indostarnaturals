import React, { useState } from 'react'
import { useCart } from '../hooks/useCart'

const CouponInput: React.FC = () => {
  const { cart, applyCoupon, removeCoupon } = useCart()
  const [couponCode, setCouponCode] = useState('')
  const [isApplying, setIsApplying] = useState(false)
  const [isRemoving, setIsRemoving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const handleApplyCoupon = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!couponCode.trim()) {
      setMessage({ type: 'error', text: 'Please enter a coupon code' })
      return
    }

    try {
      setIsApplying(true)
      setMessage(null)
      await applyCoupon(couponCode.trim())
      setMessage({ type: 'success', text: 'Coupon applied successfully!' })
      setCouponCode('')
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.error?.message || 'Invalid coupon code',
      })
    } finally {
      setIsApplying(false)
    }
  }

  const handleRemoveCoupon = async () => {
    try {
      setIsRemoving(true)
      setMessage(null)
      await removeCoupon()
      setMessage({ type: 'success', text: 'Coupon removed' })
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.error?.message || 'Failed to remove coupon',
      })
    } finally {
      setIsRemoving(false)
    }
  }

  const hasCoupon = cart?.coupon_code

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <h3 className="font-semibold text-gray-900 mb-3">Coupon Code</h3>

      {hasCoupon ? (
        <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded">
          <div>
            <p className="text-sm font-medium text-green-900">
              Coupon Applied: <span className="font-bold">{cart.coupon_code}</span>
            </p>
            <p className="text-sm text-green-700 mt-1">
              You saved ₹{cart.discount_amount.toFixed(2)}
            </p>
          </div>
          <button
            onClick={handleRemoveCoupon}
            disabled={isRemoving}
            className="text-sm text-red-600 hover:text-red-800 disabled:opacity-50"
          >
            {isRemoving ? 'Removing...' : 'Remove'}
          </button>
        </div>
      ) : (
        <form onSubmit={handleApplyCoupon} className="flex gap-2">
          <input
            type="text"
            value={couponCode}
            onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
            placeholder="Enter coupon code"
            className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500"
            disabled={isApplying}
          />
          <button
            type="submit"
            disabled={isApplying || !couponCode.trim()}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isApplying ? 'Applying...' : 'Apply'}
          </button>
        </form>
      )}

      {/* Message */}
      {message && (
        <p
          className={`text-sm mt-2 ${
            message.type === 'success' ? 'text-green-600' : 'text-red-600'
          }`}
        >
          {message.text}
        </p>
      )}
    </div>
  )
}

export default CouponInput
