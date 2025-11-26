import React, { useState } from 'react'

interface StockUpdateFormProps {
  currentStock: number
  onUpdate: (quantityDelta: number) => Promise<void>
  onCancel: () => void
}

const StockUpdateForm: React.FC<StockUpdateFormProps> = ({
  currentStock,
  onUpdate,
  onCancel,
}) => {
  const [mode, setMode] = useState<'add' | 'subtract' | 'set'>('add')
  const [quantity, setQuantity] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const calculateDelta = (): number | null => {
    const qty = parseInt(quantity, 10)
    if (isNaN(qty) || qty < 0) {
      return null
    }

    switch (mode) {
      case 'add':
        return qty
      case 'subtract':
        return -qty
      case 'set':
        return qty - currentStock
      default:
        return null
    }
  }

  const getNewStock = (): number | null => {
    const delta = calculateDelta()
    if (delta === null) return null
    return currentStock + delta
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    const delta = calculateDelta()
    if (delta === null) {
      setError('Please enter a valid quantity')
      return
    }

    const newStock = getNewStock()
    if (newStock === null || newStock < 0) {
      setError('Stock quantity cannot be negative')
      return
    }

    setLoading(true)
    try {
      await onUpdate(delta)
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to update stock')
    } finally {
      setLoading(false)
    }
  }

  const newStock = getNewStock()

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full">
      <h3 className="text-lg font-semibold mb-4">Update Stock Quantity</h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Current stock display */}
        <div className="bg-gray-50 p-3 rounded">
          <div className="text-sm text-gray-600">Current Stock</div>
          <div className="text-2xl font-bold text-gray-900">{currentStock}</div>
        </div>

        {/* Mode selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Operation
          </label>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => setMode('add')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                mode === 'add'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Add
            </button>
            <button
              type="button"
              onClick={() => setMode('subtract')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                mode === 'subtract'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Subtract
            </button>
            <button
              type="button"
              onClick={() => setMode('set')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                mode === 'set'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Set To
            </button>
          </div>
        </div>

        {/* Quantity input */}
        <div>
          <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">
            Quantity
          </label>
          <input
            type="number"
            id="quantity"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            min="0"
            step="1"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Enter quantity"
            required
          />
        </div>

        {/* Preview */}
        {quantity && newStock !== null && (
          <div className="bg-blue-50 p-3 rounded border border-blue-200">
            <div className="text-sm text-blue-800">
              <span className="font-medium">New Stock:</span>{' '}
              <span className="text-lg font-bold">{newStock}</span>
              {mode === 'add' && <span className="ml-2 text-green-600">(+{quantity})</span>}
              {mode === 'subtract' && <span className="ml-2 text-red-600">(-{quantity})</span>}
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex space-x-3 pt-2">
          <button
            type="submit"
            disabled={loading || !quantity}
            className="flex-1 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Updating...' : 'Update Stock'}
          </button>
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}

export default StockUpdateForm
