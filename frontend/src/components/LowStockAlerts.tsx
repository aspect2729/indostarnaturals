import React from 'react'
import { InventoryProduct } from '../services/analyticsService'

interface LowStockAlertsProps {
  products: InventoryProduct[]
}

const LowStockAlerts: React.FC<LowStockAlertsProps> = ({ products }) => {
  if (products.length === 0) {
    return null
  }

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6">
      <div className="flex items-start">
        <svg
          className="w-6 h-6 text-red-600 mr-3 flex-shrink-0"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fillRule="evenodd"
            d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
            clipRule="evenodd"
          />
        </svg>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-red-800 mb-2">Low Stock Alerts</h3>
          <p className="text-sm text-red-700 mb-4">
            The following products are running low on stock and need to be restocked:
          </p>
          <div className="space-y-2">
            {products.map((product) => (
              <div
                key={product.product_id}
                className="bg-white rounded-lg p-3 flex items-center justify-between"
              >
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{product.title}</p>
                  <p className="text-xs text-gray-500">SKU: {product.sku}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-red-600">
                    {product.stock_quantity} units left
                  </p>
                  <p className="text-xs text-gray-500">Restock needed</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default LowStockAlerts
