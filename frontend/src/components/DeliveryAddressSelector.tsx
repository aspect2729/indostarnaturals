import React, { useState, useEffect } from 'react'
import { Address } from '../types/user'
import userService from '../services/userService'
import AddressForm from './AddressForm'

interface DeliveryAddressSelectorProps {
  selectedAddressId: number | null
  onSelectAddress: (addressId: number) => void
}

const DeliveryAddressSelector: React.FC<DeliveryAddressSelectorProps> = ({
  selectedAddressId,
  onSelectAddress,
}) => {
  const [addresses, setAddresses] = useState<Address[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAddresses()
  }, [])

  const fetchAddresses = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await userService.getAddresses()
      setAddresses(data)
      
      // Auto-select default address if no address is selected
      if (!selectedAddressId && data.length > 0) {
        const defaultAddress = data.find((addr: Address) => addr.is_default) || data[0]
        onSelectAddress(defaultAddress.id)
      }
    } catch (err: any) {
      console.error('Failed to fetch addresses:', err)
      setError('Failed to load addresses')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAddressAdded = async (data: any) => {
    try {
      await userService.createAddress(data)
      setShowAddForm(false)
      await fetchAddresses()
    } catch (err) {
      console.error('Failed to create address:', err)
      throw err
    }
  }

  if (isLoading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
        <p className="mt-2 text-gray-600">Loading addresses...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">{error}</p>
        <button
          onClick={fetchAddresses}
          className="mt-4 text-green-600 hover:text-green-700"
        >
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-xl font-bold text-gray-900 mb-4">Delivery Address</h2>

      {addresses.length === 0 ? (
        <div className="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg">
          <p className="text-gray-600 mb-4">No saved addresses</p>
          <button
            onClick={() => setShowAddForm(true)}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            Add New Address
          </button>
        </div>
      ) : (
        <>
          <div className="space-y-3 mb-4">
            {addresses.map((address) => (
              <div
                key={address.id}
                onClick={() => onSelectAddress(address.id)}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                  selectedAddressId === address.id
                    ? 'border-green-600 bg-green-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <input
                        type="radio"
                        checked={selectedAddressId === address.id}
                        onChange={() => onSelectAddress(address.id)}
                        className="text-green-600 focus:ring-green-500"
                      />
                      <h3 className="font-semibold text-gray-900">{address.name}</h3>
                      {address.is_default && (
                        <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                          Default
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-2 ml-6">
                      {address.address_line1}
                      {address.address_line2 && `, ${address.address_line2}`}
                    </p>
                    <p className="text-sm text-gray-600 ml-6">
                      {address.city}, {address.state} {address.postal_code}
                    </p>
                    <p className="text-sm text-gray-600 ml-6">Phone: {address.phone}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={() => setShowAddForm(true)}
            className="text-green-600 hover:text-green-700 text-sm font-medium"
          >
            + Add New Address
          </button>
        </>
      )}

      {/* Add Address Form Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">Add New Address</h3>
              <button
                onClick={() => setShowAddForm(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <AddressForm
              onSubmit={handleAddressAdded}
              onCancel={() => setShowAddForm(false)}
            />
          </div>
        </div>
      )}
    </div>
  )
}

export default DeliveryAddressSelector
