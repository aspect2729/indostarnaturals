import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '../hooks/useAuth'
import userService from '../services/userService'
import AddressForm from '../components/AddressForm'
import AddressList from '../components/AddressList'
import { Address, CreateAddressRequest, UpdateUserRequest } from '../types/user'
import { useFormik } from 'formik'
import * as Yup from 'yup'

type ProfileTab = 'profile' | 'addresses'

const UserProfilePage: React.FC = () => {
  const { user, refreshUser } = useAuth()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<ProfileTab>('profile')
  const [showAddressForm, setShowAddressForm] = useState(false)
  const [editingAddress, setEditingAddress] = useState<Address | null>(null)

  // Fetch addresses
  const { data: addresses = [], isLoading: addressesLoading } = useQuery({
    queryKey: ['addresses'],
    queryFn: userService.getAddresses,
    enabled: activeTab === 'addresses',
  })

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: (data: UpdateUserRequest) => userService.updateProfile(data),
    onSuccess: () => {
      refreshUser()
      queryClient.invalidateQueries({ queryKey: ['user'] })
    },
  })

  // Create address mutation
  const createAddressMutation = useMutation({
    mutationFn: (data: CreateAddressRequest) => userService.createAddress(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['addresses'] })
      setShowAddressForm(false)
    },
  })

  // Update address mutation
  const updateAddressMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: CreateAddressRequest }) =>
      userService.updateAddress(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['addresses'] })
      setEditingAddress(null)
      setShowAddressForm(false)
    },
  })

  // Delete address mutation
  const deleteAddressMutation = useMutation({
    mutationFn: (id: number) => userService.deleteAddress(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['addresses'] })
    },
  })

  // Profile form
  const profileFormik = useFormik({
    initialValues: {
      name: user?.name || '',
      email: user?.email || '',
      phone: user?.phone || '',
    },
    enableReinitialize: true,
    validationSchema: Yup.object({
      name: Yup.string().required('Name is required'),
      email: Yup.string().email('Invalid email address'),
      phone: Yup.string().matches(/^\+?[1-9]\d{1,14}$/, 'Invalid phone number format'),
    }),
    onSubmit: async (values) => {
      await updateProfileMutation.mutateAsync(values)
    },
  })

  const handleAddressSubmit = async (data: CreateAddressRequest) => {
    if (editingAddress) {
      await updateAddressMutation.mutateAsync({ id: editingAddress.id, data })
    } else {
      await createAddressMutation.mutateAsync(data)
    }
  }

  const handleEditAddress = (address: Address) => {
    setEditingAddress(address)
    setShowAddressForm(true)
  }

  const handleCancelAddressForm = () => {
    setShowAddressForm(false)
    setEditingAddress(null)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
        <p className="mt-2 text-sm text-gray-600">Manage your account settings and addresses</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('profile')}
            className={`${
              activeTab === 'profile'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Profile Information
          </button>
          <button
            onClick={() => setActiveTab('addresses')}
            className={`${
              activeTab === 'addresses'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Addresses
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'profile' && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Profile Information</h2>
          <form onSubmit={profileFormik.handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Full Name
              </label>
              <input
                id="name"
                type="text"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-3 py-2 border"
                {...profileFormik.getFieldProps('name')}
              />
              {profileFormik.touched.name && profileFormik.errors.name && (
                <p className="mt-1 text-sm text-red-600">{profileFormik.errors.name}</p>
              )}
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-3 py-2 border"
                {...profileFormik.getFieldProps('email')}
              />
              {profileFormik.touched.email && profileFormik.errors.email && (
                <p className="mt-1 text-sm text-red-600">{profileFormik.errors.email}</p>
              )}
            </div>

            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                Phone Number
              </label>
              <input
                id="phone"
                type="tel"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-3 py-2 border"
                {...profileFormik.getFieldProps('phone')}
              />
              {profileFormik.touched.phone && profileFormik.errors.phone && (
                <p className="mt-1 text-sm text-red-600">{profileFormik.errors.phone}</p>
              )}
            </div>

            <div className="pt-4">
              <button
                type="submit"
                disabled={updateProfileMutation.isPending}
                className="w-full sm:w-auto px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {updateProfileMutation.isPending ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      )}

      {activeTab === 'addresses' && (
        <div className="space-y-6">
          {!showAddressForm && (
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-medium text-gray-900">Saved Addresses</h2>
              <button
                onClick={() => setShowAddressForm(true)}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Add New Address
              </button>
            </div>
          )}

          {showAddressForm ? (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {editingAddress ? 'Edit Address' : 'Add New Address'}
              </h3>
              <AddressForm
                address={editingAddress || undefined}
                onSubmit={handleAddressSubmit}
                onCancel={handleCancelAddressForm}
                isLoading={createAddressMutation.isPending || updateAddressMutation.isPending}
              />
            </div>
          ) : (
            <AddressList
              addresses={addresses}
              onEdit={handleEditAddress}
              onDelete={(id) => deleteAddressMutation.mutate(id)}
              isLoading={addressesLoading || deleteAddressMutation.isPending}
            />
          )}
        </div>
      )}
    </div>
  )
}

export default UserProfilePage
