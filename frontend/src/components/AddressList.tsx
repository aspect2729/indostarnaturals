import React, { useState } from 'react'
import { Address } from '../types/user'

interface AddressListProps {
  addresses: Address[]
  onEdit: (address: Address) => void
  onDelete: (id: number) => void
  isLoading?: boolean
}

const AddressList: React.FC<AddressListProps> = ({ addresses, onEdit, onDelete, isLoading }) => {
  const [deletingId, setDeletingId] = useState<number | null>(null)

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this address?')) {
      setDeletingId(id)
      try {
        await onDelete(id)
      } finally {
        setDeletingId(null)
      }
    }
  }

  if (addresses.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No addresses</h3>
        <p className="mt-1 text-sm text-gray-500">Get started by adding a new address.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {addresses.map((address) => (
        <div
          key={address.id}
          className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <h4 className="text-lg font-medium text-gray-900">{address.name}</h4>
                {address.is_default && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                    Default
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-600">{address.phone}</p>
              <p className="text-sm text-gray-600 mt-2">
                {address.address_line1}
                {address.address_line2 && `, ${address.address_line2}`}
              </p>
              <p className="text-sm text-gray-600">
                {address.city}, {address.state} {address.postal_code}
              </p>
              <p className="text-sm text-gray-600">{address.country}</p>
            </div>

            <div className="flex gap-2 ml-4">
              <button
                onClick={() => onEdit(address)}
                disabled={isLoading}
                className="text-primary-600 hover:text-primary-700 text-sm font-medium disabled:opacity-50"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(address.id)}
                disabled={isLoading || deletingId === address.id}
                className="text-red-600 hover:text-red-700 text-sm font-medium disabled:opacity-50"
              >
                {deletingId === address.id ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default AddressList
